🧠 1. Núcleo Essencial (MVP - mínimo viável)

> Foco: Jarbas funcional localmente, com histórico, personalidade e comandos simples.



[x] Processador de comandos locais (via terminal ou chat)

[x] Sistema de memória (JSONL) com limite de prompts por documento

[x] Personalidade fixa (ex: jarbas_personalidade.json)

[x] Comandos básicos: !lembrar, !resumir, !limpar

[x] Salvar histórico com ID e data para recuperar depois

[x] Limitar a carga de contexto por conversa (~20–40 prompts)



---

🗂️ 2. Núcleo Modular (nível 2 – tarefas específicas)

> Foco: Jarbas começa a agir como assistente real



[ ] Manipular arquivos locais com segurança
(somente dentro de /Jarbas/arquivos/)

[ ] Buscar arquivos com base em conteúdo (ex: "lista do mercado")

[ ] Criar lembretes com hora/data

[ ] Executar tarefas programadas (verificar lembretes a cada X minutos)

[ ] Salvar resultados de interações em pastas temáticas (notas, lembretes, tarefas)



---

🌐 3. Integrações Inteligentes (nível 3 – rede & dispositivos)

> Foco: Jarbas conectado e integrado ao mundo real



[ ] MQTT para integrar com dispositivos IoT e ESP32

[ ] Dashboard Web com controle e visualização de lembretes, arquivos e histórico

[ ] Skill para integração com Echo Show (mesmo com tela quebrada)

[ ] Conectar ao Home Assistant para ações físicas (luz, tomada, etc.)

[ ] Respostas por TTS (voz), se disponível



---

🧩 Priorização sugerida

Etapa	Objetivo	Prioridade

1	Personalidade + histórico controlado por JSONL	⭐️⭐️⭐️⭐️⭐️
2	Comandos simples !lembrar, !resumir, etc.	⭐️⭐️⭐️⭐️
3	Buscar arquivos locais por conteúdo	⭐️⭐️⭐️
4	Criar lembretes por data/hora	⭐️⭐️⭐️
5	Integração com MQTT ou Alexa	⭐️⭐️
6	Dashboard de controle visual	⭐️

Projeto Jarbas.
