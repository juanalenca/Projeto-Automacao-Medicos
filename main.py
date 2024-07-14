import time
import undetected_chromedriver as uc
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# Instalando o ChromeDriver Manager correspondente à sua versão atual
servico = Service(ChromeDriverManager().install())

# Iniciando o navegador
navegador = uc.Chrome(service=servico)

# Acessando a URL
navegador.get("https://portal.cfm.org.br/busca-medicos/?uf=PE")

# Aguardando até que o elemento esteja presente e clicável
wait = WebDriverWait(navegador, 15)


# Função para configurar a pesquisa
def configurar_pesquisa():
    while True:
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
        time.sleep(10)

        # Verificar a presença da lista de médicos através do CRM
        try:
            verificacaoMedicos = navegador.find_elements(By.XPATH, '//div[b[contains(text(), "CRM:")]]')
            if verificacaoMedicos:
                break
        except Exception as e:
            print("Elemento do CRM não encontrado, recarregando a página.")
            navegador.refresh()
            time.sleep(10)


# Função para extrair e imprimir dados de forma organizada
def extrair_e_imprimir_dados(page_num):
    print(f"Dados da página {page_num}:")

    # Extraindo os elementos individuais
    elementos_h4 = navegador.find_elements(By.TAG_NAME, 'h4')
    elementos_crm = navegador.find_elements(By.XPATH, '//div[b[contains(text(), "CRM:")]]')
    elementos_rqea = navegador.find_elements(By.XPATH, '//div[contains(@class, "col-md-12") and not(b[text()="Inscrições em outro estado:"])]')
    # Imprimindo cada tipo de dado individualmente
    print("\n--- Nomes ---")
    for h4 in elementos_h4:
        print(h4.text)

    print("\n--- CRMs ---")
    for crm in elementos_crm:
        print(crm.text.strip())

    print("\n--- Especialidades ---")
    for rqea in elementos_rqea:
        print(rqea.text.strip())

    return elementos_h4, elementos_crm, elementos_rqea


# Configurando a pesquisa
configurar_pesquisa()

# Extraindo e imprimindo dados da primeira página
elementos_h4_primeira, elementos_crm_primeira, elementos_rqea_primeira = extrair_e_imprimir_dados(1)

# Definindo a variável de controle do loop para as próximas páginas
page_num = 2

while page_num <= 2504:
    try:
        # Esperando até que os elementos de paginação estejam presentes e clicáveis
        elemento_paginacao = wait.until(EC.element_to_be_clickable(
            (By.XPATH, f'//ul/li[@class="paginationjs-page J-paginationjs-page" and @data-num="{page_num}"]')))

        if elemento_paginacao:
            elemento_paginacao.click()
            time.sleep(13)

            # Extraindo e imprimindo dados da página atual
            extrair_e_imprimir_dados(page_num)

            page_num += 1

        else:
            print(f"Não encontrou o elemento de paginação para a página {page_num}")
            break
    except Exception as e:
        print(f"Erro ao processar a página {page_num}: {e}")
        navegador.refresh()
        time.sleep(10)
        configurar_pesquisa()
        extrair_e_imprimir_dados()


# Fechando o navegador
navegador.quit()
