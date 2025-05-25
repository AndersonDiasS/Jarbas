import json
import os
import ollama

ARQUIVO_HISTORICO = "historico_jarbas.jsonl"

# Carrega o histórico a partir do arquivo
def carregar_historico():
    if not os.path.exists(ARQUIVO_HISTORICO):
        return []
    with open(ARQUIVO_HISTORICO, "r", encoding="utf-8") as f:
        return [json.loads(linha) for linha in f]

# Salva uma nova entrada no histórico
def salvar_historico(entrada):
    with open(ARQUIVO_HISTORICO, "a", encoding="utf-8") as f:
        f.write(json.dumps(entrada, ensure_ascii=False) + "\n")

# Gera a resposta do modelo com base no contexto
def gerar_resposta(historico, pergunta):
    mensagens = []

    # Adiciona memórias permanentes
    for item in historico:
        if item["tipo"] == "lembrar":
            mensagens.append({"role": "system", "content": item["conteudo"]})

    # Adiciona resumos anteriores, se existirem
    for item in historico[-10:]:
        if item["tipo"] == "resumo":
            mensagens.append({"role": "system", "content": "Resumo anterior: " + item["conteudo"]})

    # Adiciona as últimas 5 interações como contexto
    for item in historico[-10:]:
        if item["tipo"] == "mensagem":
            mensagens.append({"role": "user", "content": item["pergunta"]})
            mensagens.append({"role": "assistant", "content": item["resposta"]})

    # Adiciona a nova pergunta
    mensagens.append({"role": "user", "content": pergunta})

    resposta = ollama.chat(model="llama3", messages=mensagens)
    return resposta["message"]["content"]

# Gera um resumo do histórico
def resumir_conversa(historico):
    mensagens = [{"role": "system", "content": "Resuma a conversa a seguir em até 5 linhas."}]
    for item in historico[-10:]:
        if item["tipo"] == "mensagem":
            mensagens.append({"role": "user", "content": item["pergunta"]})
            mensagens.append({"role": "assistant", "content": item["resposta"]})
    resumo = ollama.chat(model="llama3", messages=mensagens)
    return resumo["message"]["content"]

# Início do programa Jarbas
def main():
    print("🤖 Jarbas iniciado. Pergunte algo ou use comandos como !lembrar, !resumir, !limpar, !sair.")
    historico = carregar_historico()

    while True:
        entrada = input("\nVocê: ").strip()

        if entrada.lower() == "!sair":
            print("Jarbas: Até logo!")
            break

        elif entrada.lower() == "!limpar":
            print("Jarbas: Histórico limpo (exceto memórias importantes).")
            historico = [h for h in historico if h["tipo"] == "lembrar"]
            with open(ARQUIVO_HISTORICO, "w", encoding="utf-8") as f:
                for item in historico:
                    f.write(json.dumps(item, ensure_ascii=False) + "\n")

        elif entrada.lower().startswith("!lembrar "):
            conteudo = entrada[len("!lembrar "):].strip()
            salvar_historico({"tipo": "lembrar", "conteudo": conteudo})
            historico.append({"tipo": "lembrar", "conteudo": conteudo})
            print("Jarbas: Ok, vou lembrar disso.")

        elif entrada.lower() == "!resumir":
            resumo = resumir_conversa(historico)
            salvar_historico({"tipo": "resumo", "conteudo": resumo})
            historico.append({"tipo": "resumo", "conteudo": resumo})
            print("Jarbas (resumo):", resumo)

        else:
            resposta = gerar_resposta(historico, entrada)
            print("Jarbas:", resposta)
            salvar_historico({"tipo": "mensagem", "pergunta": entrada, "resposta": resposta})
            historico.append({"tipo": "mensagem", "pergunta": entrada, "resposta": resposta})

if __name__ == "__main__":
    main()

