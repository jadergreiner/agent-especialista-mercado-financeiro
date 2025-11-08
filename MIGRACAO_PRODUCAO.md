# GUIA DE MIGRAÇÃO PARA PRODUÇÃO
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
