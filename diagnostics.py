#!/usr/bin/env python3
"""
Script para diagnosticar e resolver problemas de timeout no TTS
"""
import requests
import time
import subprocess
import os
from urllib.parse import quote

# CONFIGURAÇÃO
UMBREL_IP = "192.168.0.250"
PIPER_URL = f"http://{UMBREL_IP}:8888/api/tts"

def testar_conectividade():
    """Testa conectividade básica com o servidor"""
    print("=== TESTE DE CONECTIVIDADE ===")
    
    # Teste 1: Ping
    print(f"1. Testando ping para {UMBREL_IP}...")
    result = subprocess.run(["ping", "-c", "3", UMBREL_IP], 
                          capture_output=True, text=True)
    if result.returncode == 0:
        print("✓ Ping OK")
    else:
        print("✗ Ping falhou")
        print(result.stderr)
    
    # Teste 2: Porta
    print(f"2. Testando porta 8888...")
    try:
        response = requests.get(f"http://{UMBREL_IP}:8888", timeout=5)
        print(f"✓ Porta 8888 respondendo (status: {response.status_code})")
    except requests.exceptions.ConnectTimeout:
        print("✗ Timeout na conexão - serviço pode estar lento")
    except requests.exceptions.ConnectionError:
        print("✗ Erro de conexão - serviço pode estar offline")
    except Exception as e:
        print(f"✗ Erro: {e}")

def testar_tts_basico():
    """Testa TTS com texto simples"""
    print("\n=== TESTE TTS BÁSICO ===")
    
    textos_teste = [
        "oi",           # Muito simples
        "teste",        # Simples
        "olá mundo"     # Com acento
    ]
    
    for i, texto in enumerate(textos_teste, 1):
        print(f"{i}. Testando: '{texto}'")
        try:
            params = {'text': texto}
            start_time = time.time()
            
            response = requests.get(PIPER_URL, params=params, timeout=15)
            
            elapsed = time.time() - start_time
            print(f"   ✓ Sucesso em {elapsed:.2f}s (tamanho: {len(response.content)} bytes)")
            
        except requests.exceptions.Timeout:
            print(f"   ✗ Timeout após 15s")
        except Exception as e:
            print(f"   ✗ Erro: {e}")

def testar_tts_progressivo():
    """Testa TTS com timeouts progressivos"""
    print("\n=== TESTE COM TIMEOUTS PROGRESSIVOS ===")
    
    timeouts = [5, 10, 20, 30, 60]  # segundos
    texto = "teste de timeout"
    
    for timeout_val in timeouts:
        print(f"Testando com timeout de {timeout_val}s...")
        try:
            params = {'text': texto}
            start_time = time.time()
            
            response = requests.get(PIPER_URL, params=params, timeout=timeout_val)
            
            elapsed = time.time() - start_time
            print(f"✓ Sucesso em {elapsed:.2f}s")
            break  # Se funcionou, para aqui
            
        except requests.exceptions.Timeout:
            print(f"✗ Timeout em {timeout_val}s")
            continue
        except Exception as e:
            print(f"✗ Erro: {e}")
            break

def monitorar_tts_detalhado():
    """Monitor detalhado do TTS"""
    print("\n=== MONITOR DETALHADO ===")
    
    texto = "monitoramento detalhado"
    params = {'text': texto}
    
    print(f"URL: {PIPER_URL}")
    print(f"Parâmetros: {params}")
    print(f"URL completa: {PIPER_URL}?text={quote(texto)}")
    
    try:
        print("\nIniciando requisição...")
        start_time = time.time()
        
        response = requests.get(
            PIPER_URL, 
            params=params, 
            timeout=30,
            stream=True  # Para monitorar download
        )
        
        print(f"Status: {response.status_code}")
        print(f"Headers: {dict(response.headers)}")
        
        # Download com progresso
        content = b""
        for chunk in response.iter_content(chunk_size=1024):
            if chunk:
                content += chunk
                print(f"Baixados: {len(content)} bytes", end='\r')
        
        elapsed = time.time() - start_time
        print(f"\n✓ Concluído em {elapsed:.2f}s")
        print(f"Total: {len(content)} bytes")
        
        # Salvar para teste
        with open("teste_tts.wav", "wb") as f:
            f.write(content)
        print("Áudio salvo como 'teste_tts.wav'")
        
    except Exception as e:
        elapsed = time.time() - start_time
        print(f"\n✗ Erro após {elapsed:.2f}s: {e}")

def verificar_servico_piper():
    """Verifica se o serviço Piper está rodando corretamente"""
    print("\n=== VERIFICAÇÃO DO SERVIÇO PIPER ===")
    
    # Possíveis endpoints para verificar status
    endpoints_teste = [
        f"http://{UMBREL_IP}:8888/",
        f"http://{UMBREL_IP}:8888/health",
        f"http://{UMBREL_IP}:8888/status",
        f"http://{UMBREL_IP}:8888/api",
        f"http://{UMBREL_IP}:8888/docs"
    ]
    
    for endpoint in endpoints_teste:
        try:
            response = requests.get(endpoint, timeout=5)
            print(f"✓ {endpoint} - Status: {response.status_code}")
            if response.text and len(response.text) < 200:
                print(f"  Resposta: {response.text[:100]}")
        except Exception as e:
            print(f"✗ {endpoint} - Erro: {e}")

def sugestoes_solucao():
    """Mostra sugestões para resolver o problema"""
    print("\n" + "="*50)
    print("SUGESTÕES DE SOLUÇÃO:")
    print("="*50)
    
    print("\n1. REINICIAR SERVIÇO TTS:")
    print("   docker restart piper-tts")
    print("   # ou")
    print("   systemctl restart piper-tts")
    
    print("\n2. VERIFICAR LOGS:")
    print("   docker logs piper-tts")
    print("   # ou")
    print("   journalctl -u piper-tts -f")
    
    print("\n3. VERIFICAR RECURSOS:")
    print("   htop  # Ver CPU/RAM")
    print("   df -h # Ver espaço em disco")
    
    print("\n4. TESTAR MANUALMENTE:")
    print(f'   curl "{PIPER_URL}?text=teste" -o teste.wav --max-time 30')
    
    print("\n5. CONFIGURAR TIMEOUT MAIOR:")
    print("   # No código Python, usar timeout=60 ou mais")
    
    print("\n6. VERIFICAR FIREWALL:")
    print("   sudo ufw status")
    print("   # Liberar porta se necessário:")
    print("   sudo ufw allow 8888")

def main():
    """Executa todos os testes"""
    print("DIAGNÓSTICO COMPLETO DO SERVIÇO TTS")
    print("=" * 50)
    
    try:
        testar_conectividade()
        verificar_servico_piper()
        testar_tts_basico()
        testar_tts_progressivo()
        monitorar_tts_detalhado()
        
    except KeyboardInterrupt:
        print("\n\nTeste interrompido pelo usuário.")
    
    finally:
        sugestoes_solucao()

if __name__ == "__main__":
    main()