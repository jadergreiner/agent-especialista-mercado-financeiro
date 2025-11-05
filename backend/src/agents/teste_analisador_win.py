"""
Testes do Analisador WIN Day Trading
"""

from analisador_win_daytrading import AnalisadorWinDayTrading
import sys
from pathlib import Path

# Adicionar diretório pai ao path
sys.path.insert(0, str(Path(__file__).parent.parent))


def teste_analise_basica():
    """Teste 1: Análise básica sem input adicional"""
    print("="*70)
    print("TESTE 1: Análise Básica")
    print("="*70)
    
    analisador = AnalisadorWinDayTrading()
    resultado = analisador.analisar()
    
    print(analisador.formatar_relatorio(resultado))
    print("\n✅ Teste 1 concluído!\n")
    
    return resultado


def teste_com_checkpoint():
    """Teste 2: Análise com input adicional no checkpoint"""
    print("\n" + "="*70)
    print("TESTE 2: Análise com Checkpoint Interativo")
    print("="*70)
    
    analisador = AnalisadorWinDayTrading()
    
    # Simular informação adicional fornecida no checkpoint
    input_adicional = {
        'descricao': 'Notícia de última hora: Copom sinaliza corte de juros mais agressivo',
        'categoria': 'noticia_brasil',
        'pontos': 2,
        'impacto': 'alto'
    }
    
    print("\n💬 Usuário forneceu informação no checkpoint:")
    print(f"   '{input_adicional['descricao']}'")
    print(f"   Impacto: {input_adicional['impacto']} ({input_adicional['pontos']:+d} pontos)")
    
    resultado = analisador.analisar(dados_adicionais=input_adicional)
    
    print(analisador.formatar_relatorio(resultado))
    print("\n✅ Teste 2 concluído!\n")
    
    return resultado


def teste_configuracao_customizada():
    """Teste 3: Análise com configuração personalizada"""
    print("\n" + "="*70)
    print("TESTE 3: Configuração Customizada")
    print("="*70)
    
    config = {
        'instrumento': 'WIN',
        'contratos_inicio': 2,
        'contratos_max': 15,
        'meta_lucro': 2000.00,
        'perfil_risco': 'agressivo',
        'janela_analise_minutos': 90
    }
    
    print("\n⚙️ Configuração:")
    print(f"   Contratos inicial: {config['contratos_inicio']}")
    print(f"   Contratos máximo: {config['contratos_max']}")
    print(f"   Meta de lucro: R$ {config['meta_lucro']:,.2f}")
    print(f"   Perfil: {config['perfil_risco']}")
    
    analisador = AnalisadorWinDayTrading(config=config)
    resultado = analisador.analisar()
    
    print(analisador.formatar_relatorio(resultado))
    print("\n✅ Teste 3 concluído!\n")
    
    return resultado


def teste_analise_multipla():
    """Teste 4: Múltiplas análises (simulando updates)"""
    print("\n" + "="*70)
    print("TESTE 4: Análises Múltiplas (Updates)")
    print("="*70)
    
    analisador = AnalisadorWinDayTrading()
    
    print("\n🔄 Executando 3 análises consecutivas...\n")
    
    for i in range(1, 4):
        print(f"--- Análise #{i} ---")
        resultado = analisador.analisar()
        
        rel = resultado['relatorio_executivo']
        plano = resultado['plano_trading']
        pontuacao = resultado['pontuacao']
        
        print(f"⏰ {rel['timestamp']}")
        print(f"💰 WIN: {rel['cotacao_atual']} ({rel['variacao_dia']})")
        print(f"🎯 Saldo Macro: {rel['sintese']['saldo_macro']}")
        print(f"💼 Direção: {plano['direcao']}")
        
        if plano['direcao'] != 'AGUARDAR':
            print(f"   Entrada: {plano['entrada_inicial']['preco']:,.2f}")
            print(f"   Confiança: {plano['confianca']}/10")
        
        print()
    
    print("✅ Teste 4 concluído!\n")


def teste_extracao_yaml():
    """Teste 5: Verificar compatibilidade com modelo YAML"""
    print("\n" + "="*70)
    print("TESTE 5: Compatibilidade com Modelo YAML")
    print("="*70)
    
    analisador = AnalisadorWinDayTrading()
    resultado = analisador.analisar()
    
    # Carregar modelo YAML
        modelo_yaml = analisador.gerenciador_modelos.obter_modelo('WIN', 'rapida')
    
    print("\n📋 Verificando campos do modelo YAML:")
    print(f"   Modelo tem {len(modelo_yaml.keys())} seções principais")
    
    # Verificar se resultado tem campos esperados
    campos_modelo = ['configuracao', 'cotacao', 'analise_tecnica', 'analise_macro', 
                     'noticias', 'pontuacao', 'plano_trading']
    
    for campo in campos_modelo:
        presente = campo in modelo_yaml
        emoji = "✅" if presente else "❌"
        print(f"   {emoji} {campo}")
    
    print("\n✅ Teste 5 concluído!\n")


def menu_testes():
    """Menu interativo de testes"""
    print("\n" + "="*70)
    print("🧪 SUITE DE TESTES - ANALISADOR WIN DAY TRADING")
    print("="*70)
    print("\nEscolha um teste:")
    print("1. Análise Básica")
    print("2. Análise com Checkpoint Interativo")
    print("3. Configuração Customizada")
    print("4. Análises Múltiplas (Updates)")
    print("5. Compatibilidade YAML")
    print("6. Executar TODOS os testes")
    print("0. Sair")
    
    escolha = input("\nOpção: ")
    
    if escolha == "1":
        teste_analise_basica()
    elif escolha == "2":
        teste_com_checkpoint()
    elif escolha == "3":
        teste_configuracao_customizada()
    elif escolha == "4":
        teste_analise_multipla()
    elif escolha == "5":
        teste_extracao_yaml()
    elif escolha == "6":
        print("\n🚀 Executando TODOS os testes...\n")
        teste_analise_basica()
        teste_com_checkpoint()
        teste_configuracao_customizada()
        teste_analise_multipla()
        teste_extracao_yaml()
        print("\n" + "="*70)
        print("✅ TODOS OS TESTES CONCLUÍDOS!")
        print("="*70)
    elif escolha == "0":
        print("\n👋 Até logo!")
        return
    else:
        print("\n❌ Opção inválida!")
    
    # Perguntar se quer executar outro teste
    continuar = input("\nExecutar outro teste? (s/n): ")
    if continuar.lower() == 's':
        menu_testes()


if __name__ == "__main__":
    menu_testes()
