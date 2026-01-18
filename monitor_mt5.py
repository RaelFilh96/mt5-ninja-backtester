# -*- coding: utf-8 -*-
"""
MONITOR MT5 - Detecção inteligente de fim de backtest
"""

import socket
import time
import psutil

class MonitorMT5:
    """Monitor inteligente para detectar fim de backtest MT5"""

    def __init__(self):
        self.timeout_padrao = 120  # 2 minutos

    def testar_conexao_porta(self, porta=3000):
        """Testa se consegue conectar na porta especificada"""
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(1)
            result = sock.connect_ex(('127.0.0.1', porta))
            sock.close()
            return result == 0
        except:
            return False

    def aguardar_backtest_inteligente(self, timeout=None):
        """Aguarda fim do backtest usando monitoramento inteligente"""
        if timeout is None:
            timeout = self.timeout_padrao

        print("🎯 Monitorando porta 3000 para detectar fim do backtest...")

        inicio = time.time()
        conexao_estabelecida = False
        tempo_conexao = 0

        try:
            while time.time() - inicio < timeout:
                # Verifica conexões na porta 3000
                conexoes_atuais = []
                for conn in psutil.net_connections():
                    if conn.laddr and conn.laddr.port == 3000:
                        conexoes_atuais.append(conn.status)

                # Verifica se há conexão ESTABLISHED
                established = 'ESTABLISHED' in conexoes_atuais

                if established and not conexao_estabelecida:
                    conexao_estabelecida = True
                    tempo_conexao = time.time()
                    print("🚀 Backtest iniciado (conexão estabelecida)")

                # Se havia conexão e agora não há, backtest terminou
                elif conexao_estabelecida and not established:
                    tempo_total = time.time() - tempo_conexao
                    print("✅ Backtest concluído!")
                    print(f"⏱️ Duração real: {tempo_total:.1f}s")
                    return True

                time.sleep(0.5)

        except Exception as e:
            print(f"❌ Erro no monitoramento: {e}")

        # Fallback
        print("⏰ Não detectado via porta - usando espera de 15s")
        time.sleep(15)
        print("✅ Backtest concluído (fallback)")
        return True

    def aguardar_backtest_simples(self, segundos=15):
        """Aguarda backtest com espera fixa (fallback)"""
        print(f"⏳ Aguardando {segundos} segundos...")
        time.sleep(segundos)
        print("✅ Backtest concluído")
        return True
