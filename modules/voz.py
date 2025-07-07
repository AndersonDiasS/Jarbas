import requests
import subprocess
import os
import time
import threading
import warnings
import tempfile
from urllib.parse import quote

# Suprimir warnings
warnings.filterwarnings("ignore")

# CONFIGURAÇÃO
UMBREL_IP = "192.168.0.250"
PIPER_URL = f"http://{UMBREL_IP}:5000/api/tts"

# Cache e controle
_servidor_funcionando = None

def verificar_servidor():
    """Verificação rápida do servidor"""
    global _servidor_funcionando
    
    if _servidor_funcionando is not None:
        return _servidor_funcionando
    
    try:
        response = requests.get(f"http://{UMBREL_IP}:5000", timeout=2)
        _servidor_funcionando = True
        return True
    except:
        _servidor_funcionando = False
        return False

def falar_servidor_remoto(texto):
    """TTS remoto"""
    if not verificar_servidor():
        return False
    
    try:
        if len(texto) > 200:
            texto = texto[:200] + "..."
        
        params = {'text': texto}
        response = requests.get(PIPER_URL, params=params, timeout=10)
        
        if response.status_code != 200:
            return False
        
        audio_content = response.content
        if len(audio_content) == 0:
            return False
        
        timestamp = int(time.time())
        audio_filename = f"temp_audio_{timestamp}.wav"
        
        with open(audio_filename, "wb") as f:
            f.write(audio_content)
        
        subprocess.Popen(
            ["aplay", audio_filename],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL
        )
        
        return True
        
    except:
        global _servidor_funcionando
        _servidor_funcionando = False
        return False

def falar_google_tts(texto):
    """Google TTS - VOZ MASCULINA NATURAL"""
    try:
        from gtts import gTTS
        import pygame
        import io
        
        # Tentar diferentes configurações para voz masculina
        configuracoes_voz = [
            # Português europeu (mais grave e formal)
            {'lang': 'pt', 'slow': False, 'freq': 20000},
            # Português brasileiro com frequência reduzida
            {'lang': 'pt-br', 'slow': False, 'freq': 18000},
            # Português brasileiro normal como fallback
            {'lang': 'pt-br', 'slow': False, 'freq': 22050}
        ]
        
        for config in configuracoes_voz:
            try:
                # Criar TTS
                tts = gTTS(text=texto, lang=config['lang'], slow=config['slow'])
                
                # Salvar em buffer
                audio_buffer = io.BytesIO()
                tts.write_to_fp(audio_buffer)
                audio_buffer.seek(0)
                
                # Inicializar mixer com frequência ajustada para tom mais grave
                pygame.mixer.init(frequency=config['freq'])
                
                # Tocar áudio
                pygame.mixer.music.load(audio_buffer)
                pygame.mixer.music.play()
                
                # Aguardar terminar
                while pygame.mixer.music.get_busy():
                    time.sleep(0.1)
                
                pygame.mixer.quit()
                return True
                
            except Exception:
                # Se esta configuração falhar, tentar a próxima
                try:
                    pygame.mixer.quit()
                except:
                    pass
                continue
        
        return False
        
    except ImportError:
        return False
    except Exception as e:
        return False

def falar_espeak_melhorado(texto):
    """Espeak com VOZ MASCULINA otimizada"""
    try:
        # Configurações priorizando VOZES MASCULINAS
        configuracoes = [
            # Voz masculina brasileira grave
            ["espeak", "-v", "pt-br+m3", "-s", "160", "-p", "30", "-a", "100", "-g", "5", texto],
            # Voz masculina brasileira normal
            ["espeak", "-v", "pt-br+m1", "-s", "160", "-p", "35", "-a", "100", "-g", "3", texto],
            # Português genérico masculino
            ["espeak", "-v", "pt+m3", "-s", "160", "-p", "30", "-a", "100", texto],
            # Voz masculina genérica
            ["espeak", "-v", "m1", "-s", "150", "-p", "30", texto],
            # Fallback sem voz específica
            ["espeak", "-s", "150", "-p", "35", texto]
        ]
        
        for cmd in configuracoes:
            try:
                subprocess.run(
                    cmd,
                    stdout=subprocess.DEVNULL,
                    stderr=subprocess.DEVNULL,
                    check=True
                )
                return True
            except:
                continue
                
        return False
        
    except:
        return False

def falar_pyttsx3_melhorado(texto):
    """pyttsx3 com VOZ MASCULINA otimizada"""
    try:
        import pyttsx3
        import io
        from contextlib import redirect_stderr
        
        with redirect_stderr(io.StringIO()):
            engine = pyttsx3.init()
            
            # Configurar voz MASCULINA se disponível
            voices = engine.getProperty('voices')
            if voices:
                # Primeiro: procurar vozes explicitamente masculinas
                for voice in voices:
                    if voice and hasattr(voice, 'name'):
                        name_lower = voice.name.lower()
                        if any(term in name_lower for term in [
                            'male', 'man', 'masculin', 'joão', 'carlos', 'paulo'
                        ]):
                            engine.setProperty('voice', voice.id)
                            break
                else:
                    # Se não encontrar masculina específica, usar qualquer pt/br
                    for voice in voices:
                        if voice and hasattr(voice, 'name'):
                            name_lower = voice.name.lower()
                            if any(term in name_lower for term in ['pt', 'brazil', 'portuguese']):
                                engine.setProperty('voice', voice.id)
                                break
            
            # Configurações para voz mais grave/masculina
            engine.setProperty('rate', 160)      # Velocidade um pouco mais lenta
            engine.setProperty('volume', 1.0)    # Volume máximo
            
            engine.say(texto)
            engine.runAndWait()
            engine.stop()
        
        return True
        
    except:
        return False

def falar(texto):
    """Função principal com fallback inteligente"""
    
    # Limitar texto muito longo
    if len(texto) > 300:
        texto = texto[:300] + "..."
    
    print("🔊", end=" ", flush=True)  # Indicador visual discreto
    
    # 1. Tentar servidor remoto (mais rápido quando funciona)
    if falar_servidor_remoto(texto):
        return True
    
    # 2. Google TTS (MELHOR qualidade)
    if falar_google_tts(texto):
        return True
    
    # 3. Espeak melhorado
    if falar_espeak_melhorado(texto):
        return True
    
    # 4. pyttsx3 melhorado (último recurso)
    if falar_pyttsx3_melhorado(texto):
        return True
    
    # 5. Falha total
    print("❌ TTS indisponível")
    return False

def falar_async(texto):
    """Versão assíncrona"""
    thread = threading.Thread(target=falar, args=(texto,), daemon=True)
    thread.start()
    return thread

def teste_completo():
    """Teste das vozes"""
    print("🧪 Testando vozes disponíveis...")
    
    textos = [
        "Olá, eu sou o Jarbas",
        "Esta é minha nova voz melhorada"
    ]
    
    for texto in textos:
        print(f"Testando: {texto}")
        falar(texto)
        time.sleep(2)

if __name__ == "__main__":
    teste_completo()