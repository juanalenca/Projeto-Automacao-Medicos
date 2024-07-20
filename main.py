import time
import os
import undetected_chromedriver as uc
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# Instalando o ChromeDriver Manager correspondente à sua versão atual
servico = Service(ChromeDriverManager().install())

# Caminho para a extensão
extensao_path = 'C:\\Users\\Jhuan\\AppData\\Local\\Google\\Chrome\\User Data\\Default\\Extensions\\hlifkpholllijblknnmbfagnkjneagid\\0.2.1_0'


# Função para iniciar o navegador com a extensão
def iniciar_navegador():
    options = uc.ChromeOptions()
    options.add_argument(f'--load-extension={extensao_path}')
    return uc.Chrome(service=servico, options=options)


# Função para acessar a URL e configurar a pesquisa
def acessar_e_configurar_pesquisa(navegador):
    while True:
        try:
            navegador.get("https://portal.cfm.org.br/busca-medicos/?uf=PE")
            navegador.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            # Situação -> ativo
            time.sleep(1.5)
            navegador.find_element(By.XPATH, '//*[@id="tipoSituacao"]').click()
            time.sleep(0.5)
            navegador.find_element(By.XPATH, '//*[@id="tipoSituacao"]/option[2]').click()
            time.sleep(1)
            # Situação -> regular
            navegador.find_element(By.XPATH, '//*[@id="situacao"]').click()
            time.sleep(0.6)
            navegador.find_element(By.XPATH, '//*[@id="situacao"]/option[4]').click()
            time.sleep(1)
            # UF -> PE
            navegador.find_element(By.XPATH, '//*[@id="uf"]').click()
            time.sleep(0.55)
            navegador.find_element(By.XPATH, '//*[@id="uf"]/option[17]').click()
            time.sleep(1)
            # Enviar e aguardando o carregamento da pesquisa
            navegador.find_element(By.XPATH, '//*[@id="buscaForm"]/div/div[4]/div[2]/button').click()
            time.sleep(35)
            # Verificar a presença da lista de médicos através do CRM
            verificacaoMedicos = navegador.find_elements(By.XPATH, '//div[b[contains(text(), "CRM:")]]')
            if verificacaoMedicos:
                break
            else:
                raise Exception("Elemento do CRM não encontrado\n")
        except Exception as e:
            print("Elemento do CRM não encontrado, fechando e reabrindo a página.")
            navegador.close()
            navegador = iniciar_navegador()
            time.sleep(1)
    return navegador


# Função para extrair dados
def extrair_dados(navegador):
    elementos_h4 = navegador.find_elements(By.TAG_NAME, 'h4')
    elementos_crm = navegador.find_elements(By.XPATH, '//div[b[contains(text(), "CRM:")]]')
    elementos_rqea = navegador.find_elements(By.XPATH,
                                             '//div[contains(@class, "col-md-12") and (br or span) and not(b[text()="Inscrições em outro estado:"])]')
    return elementos_h4, elementos_crm, elementos_rqea


# Função para salvar dados de forma organizada em um arquivo .txt
def salvar_dados(elementos_h4, elementos_crm, elementos_rqea, page_num, arquivo):
    with open(arquivo, 'a', encoding='utf-8') as file:
        file.write(f"\nDados da página {page_num}:\n")
        nome_col_width = 40
        crm_col_width = 20
        especialidade_col_width = 200
        file.write(f"{'Nome':<{nome_col_width}}{'CRM':<{crm_col_width}}{'Especialidade':<{especialidade_col_width}}\n")
        file.write(f"{'-' * nome_col_width}{'-' * crm_col_width}{'-' * especialidade_col_width}\n\n")
        print(f"\nSalvando dados da página {page_num}...")
        for h4, crm, rqea in zip(elementos_h4, elementos_crm, elementos_rqea):
            file.write(
                f"{h4.text:<{nome_col_width}}{crm.text.strip():<{crm_col_width}}{rqea.text.strip():<{especialidade_col_width}}\n\n\n")
        file.write("\n")
    print(f"Dados da página {page_num} salvos com sucesso.\n\n")


# Função para ler os dados da primeira página do arquivo
def ler_dados_primeira_pagina(arquivo):
    dados_primeira_pagina = {'h4': [], 'crm': [], 'rqea': []}
    with open(arquivo, 'r', encoding='utf-8') as file:
        linhas = file.readlines()
        print(f"Lendo dados da primeira página do arquivo...\n")
        for linha in linhas:
            if linha.startswith('Nome'):
                continue
            if '-' * 40 in linha:
                break
            partes = linha.strip().split(None, 2)
            if len(partes) == 3:
                dados_primeira_pagina['h4'].append(partes[0])
                dados_primeira_pagina['crm'].append(partes[1])
                dados_primeira_pagina['rqea'].append(partes[2])
    print(f"Dados da primeira página lidos: {dados_primeira_pagina}\n\n\n")
    return dados_primeira_pagina['crm']


# Função para comparar CRMs
def comparar_dados(elementos_crm, dados_primeira_pagina_crm):
    elementos_crm_texts = [crm.text.strip() for crm in elementos_crm]

    print(f"Dados atuais da página:")
    print(f"CRM: {elementos_crm_texts}\n")

    print(f"Dados da primeira página:")
    print(f"CRM: {dados_primeira_pagina_crm}\n")

    comparacao = set(elementos_crm_texts) == set(dados_primeira_pagina_crm)

    print(f"Comparação dos CRMs resultou em: {'IDÊNTICOS :(' if comparacao else 'DIFERENTES :)'}\n\n\n")
    return comparacao


# Função para clicar no botão de paginação
def clicar_botao_paginacao(navegador, page_num):
    try:
        navegador.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        elemento_paginacao = WebDriverWait(navegador, 15).until(
            EC.element_to_be_clickable(
                (By.XPATH, f'//ul/li[@class="paginationjs-page J-paginationjs-page" and @data-num="{page_num}"]'))
        )
        time.sleep(2)
        elemento_paginacao.click()
        time.sleep(35)
        return True
    except Exception as e:
        print(f"Erro ao clicar no botão de paginação da página {page_num}: {e}")
        return False


# Iniciando o navegador e configurando a pesquisa
navegador = iniciar_navegador()
navegador = acessar_e_configurar_pesquisa(navegador)

# Definindo o caminho absoluto do arquivo onde os dados serão salvos
diretorio = 'C:\\projectPythonReciprev'
arquivo_dados = os.path.join(diretorio, 'dados_medicos.txt')

# Limpando o conteúdo do arquivo antes de iniciar
with open(arquivo_dados, 'w', encoding='utf-8') as file:
    file.write("")

# Extraindo e salvando dados da primeira página
elementos_h4_primeira, elementos_crm_primeira, elementos_rqea_primeira = extrair_dados(navegador)
salvar_dados(elementos_h4_primeira, elementos_crm_primeira, elementos_rqea_primeira, 1, arquivo_dados)

# Lendo os dados da primeira página do arquivo
dados_primeira_pagina_crm = [crm.text.strip() for crm in elementos_crm_primeira]

# Definindo a variável de controle do loop para as próximas páginas
page_num = 2

while page_num <= 2504:
    try:
        if not clicar_botao_paginacao(navegador, page_num):
            print(f"Não encontrou o elemento de paginação para a página {page_num}!\n")
            break

        # Extraindo dados da página atual
        elementos_h4_atual, elementos_crm_atual, elementos_rqea_atual = extrair_dados(navegador)

        # Comparando os CRMs da página atual com os da primeira página
        while comparar_dados(elementos_crm_atual, dados_primeira_pagina_crm):
            print(
                f"CRMs da página {page_num} são idênticos aos da primeira página. Clicando no botão da página anterior.\n\n")
            print("-" * 100)

            # Clicar na página anterior
            if not clicar_botao_paginacao(navegador, page_num - 1):
                print(f"Erro ao clicar no botão da página anterior {page_num - 1}.\n")
                break
            time.sleep(10)

            # Clicar na página atual novamente
            if not clicar_botao_paginacao(navegador, page_num):
                print(f"Erro ao clicar no botão da página atual {page_num} novamente.\n")
                break
            time.sleep(10)

            # Extraindo dados da página atual novamente
            elementos_h4_atual, elementos_crm_atual, elementos_rqea_atual = extrair_dados(navegador)

        # Salvar os dados da página atual
        salvar_dados(elementos_h4_atual, elementos_crm_atual, elementos_rqea_atual, page_num, arquivo_dados)
        page_num += 1

    except Exception as e:
        print(f"Erro ao processar a página {page_num}: {e}")
        navegador.close()
        time.sleep(5)
        navegador = iniciar_navegador()
        navegador = acessar_e_configurar_pesquisa(navegador)
        elementos_h4_primeira, elementos_crm_primeira, elementos_rqea_primeira = extrair_dados(navegador)
        salvar_dados(elementos_h4_primeira, elementos_crm_primeira, elementos_rqea_primeira, page_num, arquivo_dados)
        dados_primeira_pagina_crm = [crm.text.strip() for crm in elementos_crm_primeira]
