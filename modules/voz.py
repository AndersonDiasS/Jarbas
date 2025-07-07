import requests
import subprocess
import os
import time
import threading
from urllib.parse import quote

# CONFIGURAÇÃO
UMBREL_IP = "192.168.0.250"
PIPER_URL = f"http://{UMBREL_IP}:8888/api/tts"

# Cache para evitar requisições repetidas
_audio_cache = {}

def limpar_cache():
    """Limpa arquivos de áudio antigos"""
    try:
        for filename in os.listdir('.'):
            if filename.startswith('temp_audio_') and filename.endswith('.wav'):
                file_age = time.time() - os.path.getmtime(filename)
                if file_age > 300:  # 5 minutos
                    os.remove(filename)
    except:
        pass

def falar_com_retry(texto, max_tentativas=3):
    """Tenta falar com retry automático"""
    
    for tentativa in range(1, max_tentativas + 1):
        print(f"\nTentativa {tentativa}/{max_tentativas} - Jarbas: {texto}")
        
        try:
            # Limitar tamanho do texto
            if len(texto) > 500:
                texto = texto[:500] + "..."
                print("Texto truncado por ser muito longo")
            
            # Verificar cache
            texto_hash = hash(texto)
            if texto_hash in _audio_cache:
                audio_filename = _audio_cache[texto_hash]
                if os.path.exists(audio_filename):
                    print("Usando áudio do cache...")
                    tocar_audio(audio_filename)
                    return True
            
            # Preparar requisição
            params = {'text': texto}
            
            # Timeout progressivo: 15s, 30s, 45s
            timeout_val = 15 * tentativa
            print(f"Enviando para TTS (timeout: {timeout_val}s)...")
            
            # Requisição com timeout
            response = requests.get(
                PIPER_URL, 
                params=params, 
                timeout=timeout_val,
                stream=True  # Para detectar problemas mais cedo
            )
            
            response.raise_for_status()
            
            # Verificar se recebeu conteúdo
            if 'content-length' in response.headers:
                expected_size = int(response.headers['content-length'])
                print(f"Esperando {expected_size} bytes...")
            
            # Baixar conteúdo
            audio_content = b''
            for chunk in response.iter_content(chunk_size=8192):
                if chunk:
                    audio_content += chunk
            
            if len(audio_content) == 0:
                raise Exception("Resposta vazia do servidor TTS")
            
            print(f"Áudio recebido: {len(audio_content)} bytes")
            
            # Salvar arquivo
            timestamp = int(time.time())
            audio_filename = f"temp_audio_{timestamp}.wav"
            
            with open(audio_filename, "wb") as f:
                f.write(audio_content)
            
            # Adicionar ao cache
            _audio_cache[texto_hash] = audio_filename
            
            # Tocar áudio
            tocar_audio(audio_filename)
            
            print(f"✓ Sucesso na tentativa {tentativa}")
            return True
            
        except requests.exceptions.Timeout:
            print(f"✗ Timeout na tentativa {tentativa} ({timeout_val}s)")
            if tentativa == max_tentativas:
                print("--- FALHA FINAL: TTS não respondeu em tempo hábil ---")
                return False
            else:
                print(f"Aguardando {tentativa * 2}s antes da próxima tentativa...")
                time.sleep(tentativa * 2)
                
        except requests.exceptions.ConnectionError:
            print(f"✗ Erro de conexão na tentativa {tentativa}")
            if tentativa == max_tentativas:
                print("--- FALHA FINAL: Não foi possível conectar ao TTS ---")
                return False
            else:
                time.sleep(tentativa * 2)
                
        except Exception as e:
            print(f"✗ Erro na tentativa {tentativa}: {e}")
            if tentativa == max_tentativas:
                print("--- FALHA FINAL: Erro no processamento TTS ---")
                return False
            else:
                time.sleep(tentativa)
    
    return False

def tocar_audio(audio_filename):
    """Toca o arquivo de áudio"""
    try:
        if not os.path.exists(audio_filename):
            print(f"Arquivo {audio_filename} não encontrado")
            return False
            
        file_size = os.path.getsize(audio_filename)
        if file_size == 0:
            print(f"Arquivo {audio_filename} está vazio")
            return False
            
        print(f"Tocando {audio_filename} ({file_size} bytes)...")
        
        # Usar Popen para não travar
        process = subprocess.Popen(
            ["aplay", audio_filename],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL
        )
        
        return True
        
    except FileNotFoundError:
        print("ERRO: 'aplay' não encontrado. Instale com: sudo apt install alsa-utils")
        return False
    except Exception as e:
        print(f"Erro ao tocar áudio: {e}")
        return False

def falar_async(texto):
    """Fala em thread separada para não bloquear"""
    def _falar():
        falar_com_retry(texto)
    
    thread = threading.Thread(target=_falar, daemon=True)
    thread.start()
    return thread

def falar(texto):
    """Função principal - compatível com código existente"""
    # Limpar cache periodicamente
    if len(_audio_cache) > 10:
        limpar_cache()
    
    # Verificar se TTS está disponível rapidamente
    if not verificar_tts_rapido():
        print(f"\nJarbas (só texto): {texto}")
        print("--- TTS indisponível ---")
        return False
    
    # Tentar falar com retry
    return falar_com_retry(texto)

def verificar_tts_rapido():
    """Verificação rápida se TTS está respondendo"""
    try:
        response = requests.get(
            f"http://{UMBREL_IP}:8888", 
            timeout=3
        )
        return response.status_code in [200, 404]  # 404 também indica que servidor está vivo
    except:
        return False

def teste_tts():
    """Função para testar o TTS"""
    print("=== TESTE DO MÓDULO TTS ===")
    
    textos_teste = [
        "teste rápido",
        "este é um teste um pouco mais longo para verificar se funciona bem",
        "ção ão ãe caracteres especiais"
    ]
    
    for i, texto in enumerate(textos_teste, 1):
        print(f"\nTeste {i}: '{texto}'")
        sucesso = falar(texto)
        if sucesso:
            print("✓ Sucesso")
        else:
            print("✗ Falhou")
        
        time.sleep(2)  # Pausa entre testes

if __name__ == "__main__":
    teste_tts()