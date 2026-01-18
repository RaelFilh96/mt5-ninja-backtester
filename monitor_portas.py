#!/usr/bin/env python3
"""
Monitor de Portas - Escuta portas 3000-3015
Monitora conexões e atividade nas portas especificadas
"""

import psutil
import time
from datetime import datetime
from collections import defaultdict

class MonitorPortas:
    def __init__(self, porta_inicio=3000, porta_fim=3015):
        self.porta_inicio = porta_inicio
        self.porta_fim = porta_fim
        self.portas_monitoradas = list(range(porta_inicio, porta_fim + 1))
        self.conexoes_anteriores = {}
        self.historico_conexoes = defaultdict(list)
        
    def obter_conexoes_ativas(self):
        """Obtém todas as conexões ativas nas portas monitoradas"""
        conexoes_ativas = {}
        
        try:
            # Obter todas as conexões de rede
            conexoes = psutil.net_connections(kind='inet')
            
            for conn in conexoes:
                if conn.laddr and conn.laddr.port in self.portas_monitoradas:
                    porta = conn.laddr.port
                    
                    # Informações da conexão
                    info_conexao = {
                        'porta': porta,
                        'status': conn.status,
                        'ip_local': conn.laddr.ip,
                        'ip_remoto': conn.raddr.ip if conn.raddr else None,
                        'porta_remota': conn.raddr.port if conn.raddr else None,
                        'pid': conn.pid,
                        'processo': None
                    }
                    
                    # Tentar obter informações do processo
                    if conn.pid:
                        try:
                            processo = psutil.Process(conn.pid)
                            info_conexao['processo'] = {
                                'nome': processo.name(),
                                'cmd': ' '.join(processo.cmdline()) if processo.cmdline() else '',
                                'usuario': processo.username() if hasattr(processo, 'username') else 'N/A'
                            }
                        except (psutil.NoSuchProcess, psutil.AccessDenied):
                            info_conexao['processo'] = {'nome': 'Acesso Negado', 'cmd': '', 'usuario': 'N/A'}
                    
                    if porta not in conexoes_ativas:
                        conexoes_ativas[porta] = []
                    conexoes_ativas[porta].append(info_conexao)
                    
        except Exception as e:
            print(f"❌ Erro ao obter conexões: {e}")
            
        return conexoes_ativas
    
    def detectar_mudancas(self, conexoes_atuais):
        """Detecta mudanças nas conexões comparando com estado anterior"""
        mudancas = {
            'novas': {},
            'removidas': {},
            'alteradas': {}
        }
        
        # Detectar novas conexões
        for porta, conexoes in conexoes_atuais.items():
            if porta not in self.conexoes_anteriores:
                mudancas['novas'][porta] = conexoes
            else:
                # Comparar conexões existentes (simplificado)
                conexoes_antigas = len(self.conexoes_anteriores[porta])
                conexoes_novas = len(conexoes)
                if conexoes_novas != conexoes_antigas:
                    mudancas['alteradas'][porta] = {
                        'antes': conexoes_antigas,
                        'agora': conexoes_novas,
                        'conexoes': conexoes
                    }
        
        # Detectar conexões removidas
        for porta in self.conexoes_anteriores:
            if porta not in conexoes_atuais:
                mudancas['removidas'][porta] = self.conexoes_anteriores[porta]
        
        return mudancas
    
    def registrar_evento(self, evento, porta, detalhes):
        """Registra evento no histórico"""
        timestamp = datetime.now().strftime("%H:%M:%S.%f")[:-3]
        registro = {
            'timestamp': timestamp,
            'evento': evento,
            'detalhes': detalhes
        }
        self.historico_conexoes[porta].append(registro)
    
    def exibir_status_inicial(self):
        """Exibe status inicial das portas"""
        print("🔍 MONITOR DE PORTAS - INICIADO")
        print("=" * 60)
        print(f"📡 Monitorando portas: {self.porta_inicio} - {self.porta_fim}")
        print(f"⏰ Iniciado em: {datetime.now().strftime('%H:%M:%S')}")
        print("=" * 60)
        
        # Verificar estado inicial
        conexoes_iniciais = self.obter_conexoes_ativas()
        if conexoes_iniciais:
            print("🔌 Conexões ativas encontradas:")
            for porta, conexoes in conexoes_iniciais.items():
                print(f"  📍 Porta {porta}: {len(conexoes)} conexão(ões)")
                for conn in conexoes:
                    processo_info = ""
                    if conn['processo']:
                        processo_info = f" [{conn['processo']['nome']}]"
                    print(f"    └─  {conn['status']}{processo_info}")
        else:
            print("🔍 Nenhuma conexão ativa nas portas monitoradas")
        print()
    
    def exibir_mudancas(self, mudancas):
        """Exibe mudanças detectadas"""
        timestamp = datetime.now().strftime("%H:%M:%S.%f")[:-3]
        
        if mudancas['novas']:
            for porta, conexoes in mudancas['novas'].items():
                print(f"🆕 [{timestamp}] NOVA CONEXÃO - Porta {porta}")
                for conn in conexoes:
                    processo_info = ""
                    if conn['processo'] and conn['processo']['nome']:
                        processo_info = f" - Processo: {conn['processo']['nome']}"
                        if conn['processo']['cmd']:
                            # Mostrar apenas os primeiros 80 caracteres do comando
                            cmd_resumido = conn['processo']['cmd'][:80] + "..." if len(conn['processo']['cmd']) > 80 else conn['processo']['cmd']
                            processo_info += f" ({cmd_resumido})"
                    
                    ip_remoto = f" -> {conn['ip_remoto']}:{conn['porta_remota']}" if conn['ip_remoto'] else ""
                    print(f"    └─ {conn['ip_local']}:{conn['porta']} [{conn['status']}]{ip_remoto}{processo_info}")
                
                # NOVO: Detectar padrão de backtest (metatester64 + ESTABLISHED)
                if any(conn['processo'] and 'metatester64' in conn['processo']['nome'].lower() 
                       and conn['status'] == 'ESTABLISHED' for conn in conexoes):
                    print(f"    🎯 BACKTEST DETECTADO: MetaTrader iniciou backtest na porta {porta}")
                
                self.registrar_evento('NOVA_CONEXAO', porta, conexoes)
        
        if mudancas['removidas']:
            for porta, conexoes in mudancas['removidas'].items():
                print(f"❌ [{timestamp}] CONEXÃO REMOVIDA - Porta {porta}")
                self.registrar_evento('CONEXAO_REMOVIDA', porta, conexoes)
        
        if mudancas['alteradas']:
            for porta, info in mudancas['alteradas'].items():
                print(f"🔄 [{timestamp}] CONEXÃO ALTERADA - Porta {porta}: {info['antes']} -> {info['agora']} conexões")
                
                # NOVO: Analisar detalhes das conexões alteradas
                conexoes_atuais = info['conexoes']
                established_count = sum(1 for conn in conexoes_atuais if conn['status'] == 'ESTABLISHED')
                listen_count = sum(1 for conn in conexoes_atuais if conn['status'] == 'LISTEN')
                
                # Detectar padrões específicos
                if established_count == 0 and listen_count > 0:
                    # Possível fim de backtest: só LISTEN restou
                    if any(conn['processo'] and 'metatester64' in conn['processo']['nome'].lower() 
                           for conn in conexoes_atuais):
                        print(f"    🏁 POSSÍVEL FIM DE BACKTEST: Apenas LISTEN ativo na porta {porta}")
                
                print(f"    └─ Status atual: {established_count} ESTABLISHED, {listen_count} LISTEN")
                
                self.registrar_evento('CONEXAO_ALTERADA', porta, info)
    
    def monitorar(self, intervalo=1.0):
        """Inicia o monitoramento contínuo"""
        self.exibir_status_inicial()
        
        print("🎯 Monitoramento ativo - Pressione Ctrl+C para parar")
        print("📊 Aguardando mudanças nas conexões...")
        print("-" * 60)
        
        try:
            while True:
                conexoes_atuais = self.obter_conexoes_ativas()
                mudancas = self.detectar_mudancas(conexoes_atuais)
                
                # Exibir mudanças se houverem
                if any(mudancas.values()):
                    self.exibir_mudancas(mudancas)
                
                # Atualizar estado anterior
                self.conexoes_anteriores = conexoes_atuais.copy()
                
                time.sleep(intervalo)
                
        except KeyboardInterrupt:
            self.exibir_relatorio_final()
    
    def exibir_relatorio_final(self):
        """Exibe relatório final ao encerrar"""
        print("\n" + "=" * 60)
        print("📋 RELATÓRIO FINAL DO MONITORAMENTO")
        print("=" * 60)
        
        if self.historico_conexoes:
            for porta in sorted(self.historico_conexoes.keys()):
                eventos = self.historico_conexoes[porta]
                print(f"\n📍 Porta {porta}: {len(eventos)} evento(s)")
                for evento in eventos[-5:]:  # Mostrar últimos 5 eventos
                    print(f"  {evento['timestamp']} - {evento['evento']}")
        else:
            print("🔍 Nenhuma atividade detectada durante o monitoramento")
        
        print(f"\n⏰ Monitoramento encerrado em: {datetime.now().strftime('%H:%M:%S')}")
        print("=" * 60)

def main():
    """Função principal"""
    print("🔍 Monitor de Portas 3000-3015")
    print("Desenvolvido para debug do sistema OOS")
    print()
    
    # Criar e iniciar monitor
    monitor = MonitorPortas(porta_inicio=3000, porta_fim=3015)
    monitor.monitorar(intervalo=0.5)  # Verifica a cada 500ms para maior responsividade

if __name__ == "__main__":
    main()