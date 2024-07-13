#Projeto em desenvolvomento...
import time
import whisper
from selenium import webdriver
import undetected_chromedriver as uc
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import requests

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

    # Verificar a presença do reCAPTCHA pelo <div>
    recaptcha_divs = navegador.find_elements(By.XPATH, '//*[@id="recaptcha-token"]')
    if recaptcha_divs:
        print("reCAPTCHA detectado, iniciando resolução do áudio")
        # Esperar até que o botão de áudio esteja clicável
        audio_button = wait.until(EC.element_to_be_clickable((By.XPATH, '//*[@id="recaptcha-audio-button"]')))
        audio_button.click()
        time.sleep(2)

        # Obter o link do áudio
        audio_src = navegador.find_element(By.ID, 'audio-source').get_attribute('src')
        print(f"Link do áudio: {audio_src}")

        # Baixar o áudio
        audio_data = requests.get(audio_src).content
        with open("audio.mp3", "wb") as file:
            file.write(audio_data)

        # Usar Whisper para transcrever o áudio
        modelo = whisper.load_model("base")
        resultado = modelo.transcribe("audio.mp3")
        transcricao = resultado['text']
        print("Transcrição do áudio:", transcricao)

        # Preencher a transcrição no campo de resposta
        navegador.find_element(By.ID, 'audio-response').send_keys(transcricao)
        time.sleep(1)

        # Clicar no botão de verificação do reCAPTCHA
        navegador.find_element(By.ID, 'recaptcha-verify-button').click()
        time.sleep(2)


# Função para extrair dados
def extrair_dados():
    elementos_h4 = navegador.find_elements(By.TAG_NAME, 'h4')
    elementos_crm = navegador.find_elements(By.XPATH, '//div[b[contains(text(), "CRM:")]]')
    elementos_rqea = navegador.find_elements(By.XPATH,
                                             '//div[contains(@class, "col-md-12") and not(b[text()="Inscrições em outro estado:"])]')
    return elementos_h4, elementos_crm, elementos_rqea


# Configurando a pesquisa
configurar_pesquisa()

# Extraindo dados da primeira página
elementos_h4_primeira, elementos_crm_primeira, elementos_rqea_primeira = extrair_dados()

# Imprimindo os dados extraídos da primeira página
print("Dados da primeira página:")
for h4, crm, rqea in zip(elementos_h4_primeira, elementos_crm_primeira, elementos_rqea_primeira):
    print(h4.text, crm.text, rqea.text)

# Definindo a variável de controle do loop
page_num = 2

while page_num <= 2504:
    try:
        # Esperando até que os elementos de paginação estejam presentes e clicáveis
        elemento_paginacao = wait.until(EC.element_to_be_clickable(
            (By.XPATH, f'//ul/li[@class="paginationjs-page J-paginationjs-page" and @data-num="{page_num}"]')))

        if elemento_paginacao:
            elemento_paginacao.click()
            time.sleep(13)

            # Extraindo novos dados da página atual
            elementos_h4, elementos_crm, elementos_rqea = extrair_dados()

            # Comparando e imprimindo os dados extraídos
            print(f"Dados da página {page_num}:")
            recarregar_pagina = False
            for h4, crm, rqea, h4_primeira, crm_primeira, rqea_primeira in zip(
                    elementos_h4, elementos_crm, elementos_rqea,
                    elementos_h4_primeira, elementos_crm_primeira,
                    elementos_rqea_primeira):
                if h4.text != h4_primeira.text or crm.text != crm_primeira.text or rqea.text != rqea_primeira.text:
                    print(f"Alteração detectada na página {page_num}:")
                    print(f"Nome: {h4.text}, CRM: {crm.text}, RQEA: {rqea.text}")
                else:
                    recarregar_pagina = True
                    break

            if recarregar_pagina:
                print(f"Dados iguais aos da primeira página na página {page_num}. Recarregando a página.")
                elemento_paginacao.click()
            else:
                page_num += 1

        else:
            print(f"Não encontrou o elemento de paginação para a página {page_num}")
            break
    except Exception as e:
        print(f"Erro ao processar a página {page_num}: {e}")
        break

# Fechando o navegador
navegador.quit()
