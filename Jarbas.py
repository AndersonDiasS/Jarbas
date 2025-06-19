import requests
import json

# --- CONFIGURAÇÃO ---
# 1. Substitua esta linha pelo endereço IP do seu servidor Umbrel na sua rede local.
#    Exemplo: UMBREL_IP = "192.168.1.50"
UMBREL_IP = "192.168.0.30"

# 2. Monta a URL completa para a API do Ollama que está rodando no servidor.
OLLAMA_URL = f"http://{UMBREL_IP}:11434/api/generate"

# 3. Define qual modelo de IA queremos usar (o que você baixou anteriormente).
MODELO = "llama3:8b" 

def conversar_com_jarbas(prompt_usuario):
    """
    Esta função é o coração do programa. Ela envia a sua pergunta (prompt)
    para a IA no servidor e imprime a resposta recebida.
    """
    print("\nJarbas está pensando...")

    try:
        # Montamos o "pacote" de dados (payload) que a API do Ollama espera receber.
        # É um dicionário Python que será convertido para o formato JSON.
        payload = {
            "model": MODELO,
            "prompt": prompt_usuario,
            "stream": False  # "stream: False" significa que queremos a resposta completa de uma vez.
        }

        # Usamos a biblioteca 'requests' para enviar uma requisição POST para a nossa URL.
        # A requisição contém o nosso pacote de dados em formato JSON.
        response = requests.post(OLLAMA_URL, data=json.dumps(payload))
        
        # Esta linha verifica se a requisição foi bem-sucedida (ex: código 200 OK).
        # Se ocorrer um erro de conexão, ela lançará uma exceção.
        response.raise_for_status() 

        # A resposta da API também é em JSON. Nós a convertemos de volta para um dicionário Python.
        response_data = response.json()
        
        # Extraímos o texto da resposta que está dentro da chave "response".
        resposta_final = response_data.get("response", "Desculpe, não recebi uma resposta válida.")
        
        # Imprimimos a resposta final formatada na tela.
        print(f"\nJarbas: {resposta_final.strip()}")

    except requests.exceptions.RequestException as e:
        # Este bloco 'except' captura erros de conexão (ex: IP errado, servidor offline).
        print("\n--- ERRO DE CONEXÃO ---")
        print(f"Não foi possível conectar ao servidor Ollama em {OLLAMA_URL}")
        print("Por favor, verifique se:")
        print("1. O endereço IP está correto.")
        print("2. O seu servidor Umbrel está ligado e conectado à rede.")
        print("3. O serviço do Ollama está rodando corretamente no servidor.")
        print(f"Detalhes técnicos do erro: {e}")

# --- LOOP PRINCIPAL ---
# O código dentro deste 'if' só roda quando você executa o arquivo diretamente.
if __name__ == "__main__":
    print("--- Cliente Jarbas v1.0 ---")
    print(f"Conectando ao servidor: {UMBREL_IP}")
    print("Digite sua mensagem ou 'sair' para terminar.")
    
    # Este loop infinito mantém o chat funcionando até você digitar 'sair'.
    while True:
        # Pede para o usuário digitar uma mensagem.
        prompt = input("\nVocê: ")
        
        # Se o usuário digitar 'sair', o loop é interrompido e o programa termina.
        if prompt.lower() == 'sair':
            print("\nJarbas: Desconectando. Até a próxima.")
            break
        
        # Se não for 'sair', a função principal é chamada para processar a mensagem.
        conversar_com_jarbas(prompt)