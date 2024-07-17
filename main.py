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


# Caminho para a extensão - eh preciso pegar o ID dela
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
           time.sleep(25)


           # Verificar a presença da lista de médicos através do CRM
           verificacaoMedicos = navegador.find_elements(By.XPATH, '//div[b[contains(text(), "CRM:")]]')
           if verificacaoMedicos:
               break
           else:
               raise Exception("Elemento do CRM não encontrado")
       except Exception as e:
           print("Elemento do CRM não encontrado, fechando e reabrindo a página.")
           navegador.close()
           navegador = iniciar_navegador()
           time.sleep(1)
   return navegador



# Função para extrair e salvar dados de forma organizada em um arquivo .txt
def extrair_e_salvar_dados(navegador, page_num, arquivo):
    with open(arquivo, 'a', encoding='utf-8') as file:
        file.write(f"\nDados da página {page_num}:\n")

        # Extraindo os elementos individuais
        elementos_h4 = navegador.find_elements(By.TAG_NAME, 'h4')
        elementos_crm = navegador.find_elements(By.XPATH, '//div[b[contains(text(), "CRM:")]]')
        #elementos_rqea = navegador.find_elements(By.XPATH, '//div[contains(@class, "col-md-12") and not(b[text()="Inscrições em outro estado:"])]')
        elementos_rqea = navegador.find_elements(By.XPATH, '//div[contains(@class, "col-md-12") and (br or span) and not(b[text()="Inscrições em outro estado:"])]')

        # Definindo o tamanho das colunas
        nome_col_width = 40
        crm_col_width = 20
        especialidade_col_width = 200

        # Escrevendo os cabeçalhos da tabela
        file.write(f"{'Nome':<{nome_col_width}}{'CRM':<{crm_col_width}}{'Especialidade':<{especialidade_col_width}}\n")
        file.write(f"{'-'*nome_col_width}{'-'*crm_col_width}{'-'*especialidade_col_width}\n\n")

        # Salvando cada linha de dados individualmente
        for h4, crm, rqea in zip(elementos_h4, elementos_crm, elementos_rqea):
            file.write(f"{h4.text:<{nome_col_width}}{crm.text.strip():<{crm_col_width}}{rqea.text.strip():<{especialidade_col_width}}\n\n\n")

        file.write("\n")

    return elementos_h4, elementos_crm, elementos_rqea



# Iniciando o navegador e configurando a pesquisa
navegador = iniciar_navegador()
navegador = acessar_e_configurar_pesquisa(navegador)


# Definindo o caminho absoluto do arquivo onde os dados serão salvos
diretorio = 'C:\\Users\\Jhuan\\Documents\\ProjectDates'
arquivo_dados = os.path.join(diretorio, 'dados_medicos.txt')


# Limpando o conteúdo do arquivo antes de iniciar
with open(arquivo_dados, 'w', encoding='utf-8') as file:
    file.write("")


# Extraindo e salvando dados da primeira página
elementos_h4_primeira, elementos_crm_primeira, elementos_rqea_primeira = extrair_e_salvar_dados(navegador, 1, arquivo_dados)



# Definindo a variável de controle do loop para as próximas páginas
page_num = 2

while page_num <= 2504:
    try:
        # Esperando até que os elementos de paginação estejam presentes e clicáveis
        elemento_paginacao = WebDriverWait(navegador, 15).until(EC.element_to_be_clickable(
            (By.XPATH, f'//ul/li[@class="paginationjs-page J-paginationjs-page" and @data-num="{page_num}"]')))

        if elemento_paginacao:
            # Rolando até o final da página
            navegador.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(2)

            elemento_paginacao.click()
            time.sleep(13)

            # Extraindo e salvando dados da página atual
            extrair_e_salvar_dados(navegador, page_num, arquivo_dados)

            page_num += 1

        else:
            print(f"Não encontrou o elemento de paginação para a página {page_num}")
            break
    except Exception as e:
        print(f"Erro ao processar a página {page_num}: {e}")
        navegador.close()
        time.sleep(5)
        navegador = iniciar_navegador()
        navegador = acessar_e_configurar_pesquisa(navegador)
        extrair_e_salvar_dados(navegador, page_num, arquivo_dados)


# Fechando o navegador
navegador.quit()

