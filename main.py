import time
from selenium import webdriver
import undetected_chromedriver as webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC



# Diretório do perfil do Chrome (ajuste conforme necessário)
user_data_dir = "C:\\Users\\Jhuan\\AppData\\Local\\Google\\Chrome\\User Data"


# Instalando o ChromeDriver Manager correspondente à sua versão atual
servico = Service(ChromeDriverManager().install())


# Configurando as opções do Chrome
options = webdriver.ChromeOptions()
options.add_argument(f"user-data-dir={user_data_dir}")

options.add_argument("--no-sandbox")
options.add_argument("--disable-dev-shm-usage")
options.add_argument("--remote-debugging-port=9222")
options.add_argument("--disable-extensions")
options.add_argument("--disable-gpu")
options.add_argument("--window-size=1920,1080")
options.add_argument("--disable-software-rasterizer")
options.add_argument("--disable-plugins-discovery")
options.add_argument("--disable-dev-shm-usage")
options.add_argument("--disable-setuid-sandbox")
options.add_argument("--disable-accelerated-2d-canvas")
options.add_argument("--disable-web-security")
options.add_argument("--no-first-run")
options.add_argument("--no-default-browser-check")
options.add_argument("--disable-popup-blocking")
#options.add_argument("C:\\Users\\Jhuan\\AppData\\Local\\Google\\Chrome\\User Data\\Default\\Extensions\\ggdpplfehdighdpleoegjefnpefgpgfh\1.0.12_0\rulesets\scripting\scriptlet")



# Função para configurar a pesquisa
def configurar_pesquisa():
    # Situação -> ativo
    time.sleep(1.5)
    navegador.find_element('xpath', '//*[@id="tipoSituacao"]').click()
    time.sleep(0.5)
    navegador.find_element('xpath', '//*[@id="tipoSituacao"]/option[2]').click()
    time.sleep(1)

    # Situação -> regular
    navegador.find_element('xpath', '//*[@id="situacao"]').click()
    time.sleep(0.6)
    navegador.find_element('xpath', '//*[@id="situacao"]/option[4]').click()
    time.sleep(1)

    # UF -> PE
    navegador.find_element('xpath', '//*[@id="uf"]').click()
    time.sleep(0.55)
    navegador.find_element('xpath', '//*[@id="uf"]/option[17]').click()
    time.sleep(1)


# Iniciando o navegador com o perfil do usuário
try:
    navegador = webdriver.Chrome(service=servico, options=options)
except Exception as e:
    print(f"Erro ao iniciar o navegador: {e}")
    exit()


# Função para extrair e imprimir dados
def extrair_dados():
    elementos_h4 = navegador.find_elements(By.TAG_NAME, 'h4')
    elementos_crm = navegador.find_elements(By.XPATH, '//div[b[contains(text(), "CRM:")]]')
    elementos_rqea = navegador.find_elements(By.XPATH, '//div[contains(@class, "col-md-12") and not(b[text()="Inscrições em outro estado:"])]')
    return elementos_h4, elementos_crm, elementos_rqea



# Loop principal para garantir que a classe "card picture-left" apareça
while True:

    # Acessando a URL
    navegador.get("https://portal.cfm.org.br/busca-medicos/?uf=PE")

    # Aguardando até que o elemento esteja presente e clicável
    wait = WebDriverWait(navegador, 10)

    # Configurando a pesquisa
    configurar_pesquisa()

    # Enviar e aguardando o carregamento da pesquisa
    navegador.find_element('xpath', '//*[@id="buscaForm"]/div/div[4]/div[2]/button').click()
    time.sleep(3)

    # Verificando a presença da classe "card picture-left"
    try:
        if navegador.find_elements(By.TAG_NAME, 'h4'):
            print("Médicos não encontrados.")
            break
        else:
            navegador.refresh()  # Recarrega a página
            time.sleep(5)  # Aguarda o carregamento após a recarga
    except Exception as e:
        print(f"Erro ao verificar a classe: {e}")



# Extraindo dados da primeira página
elementos_h4_antigos, elementos_crm_antigos, elementos_rqea_antigos = extrair_dados()

# Definindo a variável de controle do loop
page_num = 2

while page_num <= 2504:
    try:
        # Esperando até que os elementos de paginação estejam presentes e clicáveis
        wait = WebDriverWait(navegador, 10)
        elemento_paginacao = wait.until(EC.element_to_be_clickable(
            (By.XPATH, f'//ul/li[@class="paginationjs-page J-paginationjs-page" and @data-num="{page_num}"]')))

        if elemento_paginacao:
            elemento_paginacao.click()
            time.sleep(10)

            # Extraindo novos dados da página atual
            elementos_h4_novos, elementos_crm_novos, elementos_rqea_novos = extrair_dados()

            # Verificando se os novos dados são diferentes dos antigos
            if (elementos_h4_novos != elementos_h4_antigos or
                    elementos_crm_novos != elementos_crm_antigos or
                    elementos_rqea_novos != elementos_rqea_antigos):

                # Atualizando os dados antigos
                #elementos_h4_antigos = elementos_h4_novos
                #elementos_crm_antigos = elementos_crm_novos
                #elementos_rqea_antigos = elementos_rqea_novos

                # Extrair e imprimir os dados
                extrair_dados()
                print(extrair_dados())

                page_num += 1
            else:
                print(f"Os dados da página {page_num} são iguais aos da página anterior. Tentando novamente.")
                elemento_paginacao.click()  # Clicar novamente na paginação
                time.sleep(10)
        else:
            print(f"Não encontrou o elemento de paginação para a página {page_num}")
            break
    except Exception as e:
        print(f"Erro ao processar a página {page_num}: {e}")
        break



# Fechando o navegador
navegador.quit()



