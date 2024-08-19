import pandas as pd
import requests
import telebot

def acoes_setor(setor=None):
    """
    Setores:
      1 - Agropecuária
      2 - Água e Saneamento
      3 - Alimentos Processados
      4 - Serv.Méd.Hospit. Análises e Diagnósticos
      5 - Automóveis e Motocicletas
      6 - Bebidas
      7 - Comércio
      8 - Comércio e Distribuição
      9 - Computadores e Equipamentos
      10 - Construção Civil
      11 - Construção e Engenharia
      12 - Diversos
      13 - 
      14 - Energia Elétrica
      15 - Equipamentos
      16 - Exploração de Imóveis
      17 - Gás
      18 - Holdings Diversificadas
      19 - Hoteis e Restaurantes
      20 - Intermediários Financeiros
      21 - Madeira e Papel
      22 - Máquinas e Equipamentos
      23 - Materiais Diversos
      24 - Material de Transporte
      25 - Medicamentos e Outros Produtos
      26 - Mídia
      27 - Mineração
      28 - Outros
      29 - 
      30 - Petróleo, Gás e Biocombustíveis
      31 - Previdência e Seguros
      32 - Produtos de Uso Pessoal e de Limpeza
      33 - Programas e Serviços
      34 - Químicos
      35 - 
      36 - Serviços Diversos
      37 - Serviços Financeiros Diversos
      38 - Siderurgia e Metalurgia
      39 - Tecidos, Vestuário e Calçados
      40 - Telecomunicações
      41 - Transporte
      42 - Utilidades Domésticas
      43 - Viagens e Lazer
    
    Output:
      List
    """

    ## GET: setor
    url = f'http://www.fundamentus.com.br/resultado.php?setor={setor}'
    header = {'User-agent': 'Mozilla/5.0 (Windows; U; Windows NT 6.1; rv:2.2) Gecko/20110201' ,
           'Accept': 'text/html, text/plain, text/css, text/sgml, */*;q=0.01' ,
           'Accept-Encoding': 'gzip, deflate' ,
           }
    r = requests.get(url, headers=header)
    df = pd.read_html(r.text,  decimal=',', thousands='.')[0]
    return list(df['Papel'])
  
#IMPORTANDO DADOS DAS EMPRESAS
url = 'http://www.fundamentus.com.br/resultado.php'
header = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/84.0.4147.89 Safari/537.36"}
r = requests.get(url, headers=header)
tabela = pd.read_html(r.text,  decimal=',', thousands='.')[0]

#TRATANDO DADOS
for coluna in ['Div.Yield', 'Mrg Ebit', 'Mrg. Líq.', 'ROIC', 'ROE', 'Cresc. Rec.5a']:
  tabela[coluna] = tabela[coluna].str.replace('.', '')
  tabela[coluna] = tabela[coluna].str.replace(',', '.')
  tabela[coluna] = tabela[coluna].str.rstrip('%').astype('float') / 100

#CRIANDO RANKING
liquidez = 1000000
qtd_ativos = 15
tabela = tabela[['Papel', 'Cotação', 'EV/EBIT', 'ROIC', 'Liq.2meses', 'P/L']]
tabela['Empresa'] = tabela['Papel'].str[:4]

interm_finan = acoes_setor(20)
prev_seg = acoes_setor(31)
empresas_fora = interm_finan + prev_seg
mascara = tabela['Papel'].isin(empresas_fora)
tabela = tabela[~mascara]

tabela = tabela.drop_duplicates(subset='Empresa')
tabela = tabela.set_index('Papel')
tabela = tabela[tabela['Liq.2meses'] > liquidez]
tabela = tabela[tabela['P/L'] > 0]
tabela = tabela[tabela['EV/EBIT'] > 0]
tabela = tabela[tabela['ROIC'] > 0]
tabela = tabela.drop(columns = ['Empresa', 'P/L', 'Liq.2meses'])
tabela['RANKING_EV/EBIT'] = tabela['EV/EBIT'].rank(ascending = True)
tabela['RANKING_ROIC'] = tabela['ROIC'].rank(ascending = False)
tabela['RANKING_TOTAL'] = tabela['RANKING_EV/EBIT'] + tabela['RANKING_ROIC']
tabela = tabela.sort_values('RANKING_TOTAL')
tabela = tabela.head(qtd_ativos)

ranking = tabela.index
ranking = '\n'.join(f'{i+1}. {acao}' for i, acao in enumerate(ranking))

#ENVIANDO MENSAGEM PARA TELEGRAM COM O RANKING
mensagem = f'RANKING DA MAGIC FORMULA:\n{ranking}'
print(mensagem)
bot = telebot.TeleBot("YOUR BOT HERE")
group = "YOUR GROUP HERE"
bot.send_message(group, mensagem)
