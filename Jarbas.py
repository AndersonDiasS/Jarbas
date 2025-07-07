import requests
import json
import time
from modules import voz

# --- CONFIGURAÇÃO ---
UMBREL_IP = "192.168.0.250"
OLLAMA_URL = f"http://{UMBREL_IP}:11434/api/generate"
MODELO = "llama3:8b"

def conversar_com_jarbas(prompt_usuario):
    """Conversa limpa com Jarbas"""
    print(f"\n🤔 Pensando...")
    
    try:
        payload = {
            "model": MODELO,
            "prompt": prompt_usuario,
            "stream": False
        }
        
        headers = {'Content-Type': 'application/json'}
        
        response = requests.post(
            OLLAMA_URL, 
            data=json.dumps(payload),
            headers=headers,
            timeout=30
        )
        
        response.raise_for_status()
        response_data = response.json()
        
        resposta_em_texto = response_data.get("response", "Desculpe, não consegui pensar em uma resposta.")
        
        if not resposta_em_texto or resposta_em_texto.strip() == "":
            resposta_em_texto = "Recebi uma resposta vazia do servidor."
        
        # Limpar a resposta e falar
        resposta_limpa = resposta_em_texto.strip()
        print(f"\n🤖 Jarbas: {resposta_limpa}")
        voz.falar(resposta_limpa)
        
    except requests.exceptions.Timeout:
        erro_msg = "Timeout: Demorei muito para responder."
        print(f"\n❌ {erro_msg}")
        voz.falar(erro_msg)
        
    except requests.exceptions.ConnectionError:
        erro_msg = "Erro de conexão com o servidor."
        print(f"\n❌ {erro_msg}")
        voz.falar(erro_msg)
        
    except Exception as e:
        erro_msg = "Ocorreu um erro inesperado."
        print(f"\n❌ {erro_msg}")
        voz.falar(erro_msg)

def testar_conexao():
    """Teste silencioso"""
    try:
        response = requests.get(f"http://{UMBREL_IP}:11434/api/tags", timeout=5)
        return response.status_code == 200
    except:
        return False

# --- LOOP PRINCIPAL ---
if __name__ == "__main__":
    print("🤖 === JARBAS ONLINE ===")
    
    # Teste de conexão
    if testar_conexao():
        print("✅ Servidor online")
    else:
        print("⚠️  Servidor pode estar offline")
    
    voz.falar("Jarbas online.")
    
    while True:
        try:
            prompt = input("\n💭 Você: ")
            
            if prompt.lower() in ['sair', 'quit', 'exit', 'tchau']:
                voz.falar("Até logo!")
                break
            
            if prompt.strip() == "":
                continue
                
            conversar_com_jarbas(prompt)
            
        except KeyboardInterrupt:
            print("\n\n👋 Tchau!")
            voz.falar("Desconectando.")
            break
        except Exception as e:
            print(f"❌ Erro: {e}")
            continue