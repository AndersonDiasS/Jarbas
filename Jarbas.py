import requests
import json
import time
from modules import voz

# --- CONFIGURAÇÃO ---
UMBREL_IP = "192.168.0.250"
OLLAMA_URL = f"http://{UMBREL_IP}:11434/api/generate"
MODELO = "llama3:8b"

def conversar_com_jarbas(prompt_usuario):
    """
    Envia a pergunta do usuário para a IA Ollama e usa o módulo 'voz'
    para falar a resposta.
    """
    print("\nJarbas está pensando...")
    
    try:
        payload = {
            "model": MODELO,
            "prompt": prompt_usuario,
            "stream": False
        }
        
        # Adicionar headers apropriados
        headers = {
            'Content-Type': 'application/json'
        }
        
        print(f"Enviando requisição para: {OLLAMA_URL}")
        print(f"Payload: {json.dumps(payload, indent=2)}")
        
        # Adicionar timeout para evitar travamento
        response = requests.post(
            OLLAMA_URL, 
            data=json.dumps(payload),
            headers=headers,
            timeout=30  # Timeout de 30 segundos
        )
        
        print(f"Status da resposta: {response.status_code}")
        
        response.raise_for_status()
        response_data = response.json()
        
        print(f"Resposta recebida: {response_data}")
        
        resposta_em_texto = response_data.get("response", "Desculpe, não consegui pensar em uma resposta.")
        
        # Verificar se a resposta não está vazia
        if not resposta_em_texto or resposta_em_texto.strip() == "":
            resposta_em_texto = "Recebi uma resposta vazia do servidor."
        
        print(f"Texto para falar: {resposta_em_texto[:100]}...")  # Mostrar primeiros 100 chars
        voz.falar(resposta_em_texto.strip())
        
    except requests.exceptions.Timeout:
        erro_msg = "Timeout: O servidor demorou muito para responder."
        print(f"\n--- ERRO DE TIMEOUT ---")
        print(erro_msg)
        voz.falar(erro_msg)
        
    except requests.exceptions.ConnectionError:
        erro_msg = f"Erro de conexão: Não foi possível conectar ao servidor {OLLAMA_URL}"
        print(f"\n--- ERRO DE CONEXÃO ---")
        print(erro_msg)
        voz.falar(erro_msg)
        
    except requests.exceptions.HTTPError as e:
        erro_msg = f"Erro HTTP {response.status_code}: {str(e)}"
        print(f"\n--- ERRO HTTP ---")
        print(erro_msg)
        print(f"Resposta do servidor: {response.text}")
        voz.falar("Erro na comunicação com o servidor.")
        
    except json.JSONDecodeError:
        erro_msg = "Erro ao decodificar a resposta JSON do servidor."
        print(f"\n--- ERRO JSON ---")
        print(erro_msg)
        print(f"Resposta recebida: {response.text}")
        voz.falar(erro_msg)
        
    except Exception as e:
        erro_msg = f"Erro inesperado: {str(e)}"
        print(f"\n--- ERRO GERAL ---")
        print(erro_msg)
        voz.falar("Ocorreu um erro inesperado.")

def testar_conexao():
    """
    Testa se o servidor Ollama está respondendo
    """
    try:
        print(f"Testando conexão com {OLLAMA_URL}...")
        response = requests.get(f"http://{UMBREL_IP}:11434/api/tags", timeout=5)
        if response.status_code == 200:
            print("✓ Servidor Ollama está online")
            return True
        else:
            print(f"✗ Servidor retornou status {response.status_code}")
            return False
    except Exception as e:
        print(f"✗ Erro ao testar conexão: {e}")
        return False

# --- LOOP PRINCIPAL ---
if __name__ == "__main__":
    print("--- Cliente Jarbas ---")
    print(f"Servidor: {UMBREL_IP}")
    
    # Testar conexão antes de iniciar
    if not testar_conexao():
        print("AVISO: Não foi possível conectar ao servidor Ollama")
        print("Continuando mesmo assim...")
    
    voz.falar("Jarbas online. Pronto para receber seus comandos.")
    
    while True:
        try:
            prompt = input("\nVocê: ")
            
            if prompt.lower() in ['sair', 'quit', 'exit']:
                voz.falar("Desconectando.")
                break
            
            if prompt.strip() == "":
                print("Digite algo ou 'sair' para encerrar.")
                continue
                
            conversar_com_jarbas(prompt)
            
        except KeyboardInterrupt:
            print("\n\nInterrompido pelo usuário.")
            voz.falar("Desconectando.")
            break
        except Exception as e:
            print(f"Erro no loop principal: {e}")
            continue