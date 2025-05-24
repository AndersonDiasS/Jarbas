import requests, json, time

HISTORICO = "historico.jsonl"

def perguntar_ao_jarbas(pergunta):
    res = requests.post("http://localhost:11434/api/generate", json={
        "model": "llama3",
        "prompt": pergunta,
        "stream": False
    })
    resposta = res.json().get("response", "[Erro ao responder]")
    salvar(pergunta, resposta)
    return resposta

def salvar(prompt, resposta):
    with open(HISTORICO, "a") as f:
        f.write(json.dumps({
            "timestamp": time.time(),
            "pergunta": prompt,
            "resposta": resposta
        }) + "\n")

print("🤖 Jarbas iniciado! (digite 'sair' para encerrar)")
while True:
    entrada = input("Você: ")
    if entrada.lower() in ["sair", "exit", "quit"]:
        print("👋 Encerrando Jarbas.")
        break
    resposta = perguntar_ao_jarbas(entrada)
    print("Jarbas:", resposta)
