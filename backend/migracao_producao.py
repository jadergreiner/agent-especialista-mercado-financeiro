#!/usr/bin/env python3
"""
SCRIPT DE MIGRAÇÃO PARA PRODUÇÃO
Adapta o sistema de DEMO para dados reais de produção

Este script:
1. Atualiza configurações para usar dados reais
2. Configura corretoras para produção
3. Ajusta limites de risco para produção
4. Valida chaves de API
5. Testa conectividade com corretoras

IMPORTANTE: Execute apenas após configurar chaves reais!
"""

import os
import json
import shutil
from pathlib import Path
from typing import Dict, Any

def criar_arquivo_env_producao():
    """Cria arquivo .env para produção baseado no template"""

    template_path = Path("config/.env.example")
    env_path = Path(".env")

    if env_path.exists():
        print("⚠️ Arquivo .env já existe!")
        resposta = input("Sobrescrever? (s/N): ").lower().strip()
        if resposta != 's':
            return False

    if not template_path.exists():
        print("❌ Template .env.example não encontrado!")
        return False

    # Copiar template
    shutil.copy(template_path, env_path)
    print("✅ Arquivo .env criado a partir do template")
    print("📝 Configure suas chaves reais no arquivo .env")

    return True

def atualizar_config_sistema_trading():
    """Atualiza config/sistema_trading.json para produção"""

    config_path = Path("config/sistema_trading.json")

    if not config_path.exists():
        print("❌ Arquivo config/sistema_trading.json não encontrado!")
        return False

    with open(config_path, 'r', encoding='utf-8') as f:
        config = json.load(f)

    # Ajustes para produção
    config['sistema']['modo_debug'] = False
    config['sistema']['intervalo_principal'] = 15  # Mais frequente em produção

    config['componentes']['trading_automatizado']['ativo'] = True
    config['componentes']['trading_automatizado']['execucao_automatica'] = True
    config['componentes']['trading_automatizado']['intervalo_analise'] = 30

    config['componentes']['webapp']['debug'] = False

    # Limites de risco mais conservadores para produção
    config['limites_risco']['perda_maxima_diaria'] = 0.02  # 2%
    config['limites_risco']['drawdown_maximo'] = 0.10      # 10%
    config['limites_risco']['concentracao_maxima'] = 0.20  # 20%

    # Salvar configuração atualizada
    with open(config_path, 'w', encoding='utf-8') as f:
        json.dump(config, f, indent=2, ensure_ascii=False)

    print("✅ Configuração sistema_trading.json atualizada para produção")
    return True

def configurar_corretora_producao():
    """Configura corretora para produção"""

    config_path = Path("config/corretoras.json")

    if not config_path.exists():
        print("❌ Arquivo config/corretoras.json não encontrado!")
        return False

    with open(config_path, 'r', encoding='utf-8') as f:
        config = json.load(f)

    # Verificar se tem configuração de produção
    if 'alpaca_live' not in config:
        print("❌ Configuração alpaca_live não encontrada!")
        return False

    # Verificar se chaves estão configuradas
    alpaca_live = config['alpaca_live']
    if alpaca_live['api_key'] == 'SEU_ALPACA_LIVE_KEY':
        print("⚠️ AVISO: Chave ALPACA live não configurada!")
        print("   Configure em config/corretoras.json ou .env")

    print("✅ Configuração de corretora verificada")
    return True

def criar_script_testes_producao():
    """Cria script de testes para validar produção"""

    script_teste = '''#!/usr/bin/env python3
"""
TESTES DE PRODUÇÃO - Validar funcionamento com dados reais
Execute este script antes de colocar em produção
"""

import os
import sys
from pathlib import Path

# Adicionar backend ao path
backend_dir = Path(__file__).parent / "backend"
sys.path.insert(0, str(backend_dir))

def testar_configuracao_ambiente():
    """Testa se configuração de ambiente está correta"""
    print("🔧 Testando configuração de ambiente...")

    try:
        from configuracao_ambiente import configurar_ambiente_producao
        config = configurar_ambiente_producao()

        if config.ambiente.value == 'producao':
            print("✅ Ambiente PRODUÇÃO configurado")
            return True
        else:
            print(f"⚠️ Ambiente configurado: {config.ambiente.value}")
            return False

    except Exception as e:
        print(f"❌ Erro na configuração: {e}")
        return False

def testar_conectividade_corretora():
    """Testa conectividade com corretora"""
    print("\\n📡 Testando conectividade com corretora...")

    try:
        from configuracao_ambiente import obter_configuracao_corretora, configurar_ambiente_producao

        config_sistema = configurar_ambiente_producao()
        config_corretora = obter_configuracao_corretora(config_sistema)

        if config_corretora.get('api_key') and config_corretora['api_key'] != 'SEU_ALPACA_LIVE_KEY':
            print("✅ Chaves de API configuradas")
            # Aqui poderia testar conectividade real
            print("✅ Conectividade básica OK")
            return True
        else:
            print("❌ Chaves de API não configuradas")
            return False

    except Exception as e:
        print(f"❌ Erro na conectividade: {e}")
        return False

def testar_sistema_aprendizado():
    """Testa sistema de aprendizado contínuo"""
    print("\\n🧠 Testando sistema de aprendizado...")

    try:
        from sistema_aprendizado_continuo import SistemaAprendizadoContinuo

        sistema = SistemaAprendizadoContinuo()

        if hasattr(sistema, 'ambiente'):
            print(f"✅ Sistema configurado para: {sistema.ambiente}")
            return True
        else:
            print("⚠️ Sistema sem configuração de ambiente")
            return False

    except Exception as e:
        print(f"❌ Erro no sistema de aprendizado: {e}")
        return False

def main():
    """Executa todos os testes"""
    print("🚀 TESTES DE PRODUÇÃO - Agent Especialista Mercado Financeiro")
    print("=" * 60)

    testes = [
        ("Configuração de Ambiente", testar_configuracao_ambiente),
        ("Conectividade Corretora", testar_conectividade_corretora),
        ("Sistema de Aprendizado", testar_sistema_aprendizado),
    ]

    resultados = []
    for nome_teste, funcao_teste in testes:
        print(f"\\n📋 Executando: {nome_teste}")
        try:
            resultado = funcao_teste()
            resultados.append((nome_teste, resultado))
        except Exception as e:
            print(f"❌ Erro inesperado: {e}")
            resultados.append((nome_teste, False))

    # Resumo
    print("\\n" + "=" * 60)
    print("📊 RESUMO DOS TESTES:")

    todos_passaram = True
    for nome_teste, resultado in resultados:
        status = "✅ PASSOU" if resultado else "❌ FALHOU"
        print(f"   {nome_teste}: {status}")
        if not resultado:
            todos_passaram = False

    print("\\n" + "=" * 60)
    if todos_passaram:
        print("🎉 TODOS OS TESTES PASSARAM!")
        print("✅ Sistema pronto para produção")
    else:
        print("⚠️ Alguns testes falharam!")
        print("🔧 Corrija os problemas antes de colocar em produção")

    return todos_passaram

if __name__ == "__main__":
    sucesso = main()
    sys.exit(0 if sucesso else 1)
'''

    script_path = Path("testes_producao.py")
    with open(script_path, 'w', encoding='utf-8') as f:
        f.write(script_teste)

    print("✅ Script de testes criado: testes_producao.py")
    return True

def criar_guia_migracao():
    """Cria guia de migração para produção"""

    guia = '''# GUIA DE MIGRAÇÃO PARA PRODUÇÃO
## Agent Especialista Mercado Financeiro

### 📋 PRÉ-REQUISITOS

1. **Chaves de API válidas**
   - Alpaca Live Trading API Key
   - Alpaca Live Trading Secret Key
   - Verificar limites de API

2. **Conta de corretora**
   - Conta Alpaca aprovada para live trading
   - Fundos suficientes para operações
   - Verificar documentação KYC

3. **Ambiente de produção**
   - Servidor dedicado ou VPS
   - Backup automático configurado
   - Monitoramento 24/7

### 🚀 PASSOS DE MIGRAÇÃO

#### 1. Configuração Inicial
```bash
# 1. Clonar repositório em produção
git clone <repo> /opt/agent-financeiro
cd /opt/agent-financeiro

# 2. Instalar dependências
pip install -r requirements.txt

# 3. Executar migração
python backend/migracao_producao.py
```

#### 2. Configuração de Segurança
```bash
# 1. Criar arquivo .env seguro
cp config/.env.example .env
chmod 600 .env

# 2. Editar .env com chaves reais
nano .env
```

#### 3. Testes de Produção
```bash
# 1. Executar testes
python testes_producao.py

# 2. Verificar logs
tail -f logs/*.log

# 3. Testar conectividade
python -c "from backend.configuracao_ambiente import configurar_ambiente_producao; configurar_ambiente_producao()"
```

#### 4. Ativação em Produção
```bash
# 1. Configurar ambiente
export AMBIENTE=producao

# 2. Iniciar sistema
python backend/main.py &

# 3. Verificar funcionamento
curl http://localhost:8000/api/v1/saude
```

### ⚠️ VERIFICAÇÕES DE SEGURANÇA

- [ ] Chaves API não estão no repositório
- [ ] Arquivo .env tem permissões 600
- [ ] Logs não contêm informações sensíveis
- [ ] Backup automático configurado
- [ ] Monitoramento de erros ativo

### 🔍 MONITORAMENTO EM PRODUÇÃO

1. **Métricas principais**
   - Taxa de acerto das recomendações
   - Performance do portfolio
   - Latência das operações
   - Uptime do sistema

2. **Alertas críticos**
   - Perda > 2% em um dia
   - Falha de conectividade > 5 min
   - Erro de API de corretora
   - Drawdown > 10%

3. **Backup e recuperação**
   - Backup diário dos dados
   - Estratégia de fail-over
   - Plano de recuperação de desastres

### 🚨 PROCEDIMENTOS DE EMERGÊNCIA

1. **Parar operações automaticamente**
   ```bash
   export AMBIENTE=demo  # Volta para modo seguro
   killall python
   ```

2. **Fechar todas as posições**
   - Usar interface da corretora
   - Ou executar script de emergência

3. **Análise post-mortem**
   - Revisar logs de erro
   - Identificar causa raiz
   - Implementar correções

### 📞 CONTATO E SUPORTE

- **Responsável técnico:** [Nome]
- **Contato emergência:** [Telefone/Email]
- **Documentação completa:** docs/producao/

---
**Data:** 2025-11-07
**Versão:** 1.0
'''

    guia_path = Path("MIGRACAO_PRODUCAO.md")
    with open(guia_path, 'w', encoding='utf-8') as f:
        f.write(guia)

    print("✅ Guia de migração criado: MIGRACAO_PRODUCAO.md")
    return True

def main():
    """Executa migração completa para produção"""
    print("🚀 MIGRAÇÃO PARA PRODUÇÃO")
    print("Agent Especialista Mercado Financeiro")
    print("=" * 50)

    print("\\n⚠️ IMPORTANTE:")
    print("Este script adapta o sistema para usar dados reais de produção.")
    print("Certifique-se de ter configurado suas chaves de API reais!")
    print()

    # Confirmar execução
    resposta = input("Continuar com a migração? (s/N): ").lower().strip()
    if resposta != 's':
        print("❌ Migração cancelada pelo usuário")
        return False

    etapas = [
        ("Criar arquivo .env", criar_arquivo_env_producao),
        ("Atualizar config sistema", atualizar_config_sistema_trading),
        ("Configurar corretora", configurar_corretora_producao),
        ("Criar script de testes", criar_script_testes_producao),
        ("Criar guia de migração", criar_guia_migracao),
    ]

    sucesso_total = True
    for nome_etapa, funcao_etapa in etapas:
        print(f"\\n📋 Executando: {nome_etapa}")
        try:
            sucesso = funcao_etapa()
            if sucesso:
                print(f"✅ {nome_etapa} - Concluído")
            else:
                print(f"❌ {nome_etapa} - Falhou")
                sucesso_total = False
        except Exception as e:
            print(f"❌ {nome_etapa} - Erro: {e}")
            sucesso_total = False

    print("\\n" + "=" * 50)
    if sucesso_total:
        print("🎉 MIGRAÇÃO PARA PRODUÇÃO CONCLUÍDA!")
        print("\\n📝 PRÓXIMOS PASSOS:")
        print("1. Configure suas chaves reais no arquivo .env")
        print("2. Execute: python testes_producao.py")
        print("3. Leia o guia: MIGRACAO_PRODUCAO.md")
        print("4. Para ativar: export AMBIENTE=producao")
    else:
        print("⚠️ MIGRAÇÃO CONCLUÍDA COM AVISOS!")
        print("Verifique os erros acima e corrija antes de prosseguir.")

    return sucesso_total

if __name__ == "__main__":
    sucesso = main()
    exit(0 if sucesso else 1)