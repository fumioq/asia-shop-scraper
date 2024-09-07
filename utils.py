import requests
from bs4 import BeautifulSoup
import json
import html
from classes import Product
from selenium import webdriver
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.remote.errorhandler import MoveTargetOutOfBoundsException
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import re

from time import sleep

HEADERS = {
    "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
    "accept-language": "pt-BR,pt;q=0.9,en-US;q=0.8,en;q=0.7",
    "cache-control": "max-age=0",
    "if-modified-since": "Tue, 20 Aug 2024 19:39:28 GMT",
    "if-none-match": "d168126edc2013b5609bb6940c88267519a7dc9e",
    "priority": "u=0, i",
    "sec-ch-ua": "\"Not)A;Brand\";v=\"99\", \"Google Chrome\";v=\"127\", \"Chromium\";v=\"127\"",
    "sec-ch-ua-mobile": "?0",
    "sec-ch-ua-platform": "\"Windows\"",
    "sec-fetch-dest": "document",
    "sec-fetch-mode": "navigate",
    "sec-fetch-site": "same-origin",
    "sec-fetch-user": "?1",
    "upgrade-insecure-requests": "1",
    "user-agent" : "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/127.0.0.0 Safari/537.36",
}


# def get_data(now_str) -> list:
#     data = scrape_data()
#     structured_data = [Product(product, now_str) for product in data]
#     filtered_data = [product for product in structured_data if product.is_valid()]
#     new_data = [product.get_output() for product in filtered_data]

#     return new_data


def get_data(now_str) -> list:
    data = scrape_data_selenium(now_str)
    return data


def scrape_data_selenium(now_str) -> list:
    ffOptions = Options()
    ffOptions.add_argument("-headless")

    driver = webdriver.Firefox(options=ffOptions)
    actions_chains = webdriver.ActionChains(driver)

    print('Webdriver ok!')

    driver.get('https://www.asiashop.com.br/categoria/temperos-orientais?pag=1')

    element = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.CSS_SELECTOR, 'span[class="cookiewarning-btn"]'))
    )

    print('Page loaded successfully. Loading pages...')

    element.click()
    fully_loaded = False
    try_count = 3 # Quantidade de vezes que o robô irá procurar pelo botão de carregar mais antes de considerar que acabou


    while not fully_loaded:
        if try_count > 10:
            fully_loaded = True

        try:
            next_page_button = driver.find_element(By.CLASS_NAME, 'estNextPageButFC')
            actions_chains.scroll_by_amount(0, 2000).perform()
            next_page_button.click()
            try_count = 0
            sleep(2)

        except (MoveTargetOutOfBoundsException,NoSuchElementException):
            actions_chains.scroll_by_amount(0, 2000).perform()
            try_count += 1
            sleep(1)

    print('All pages loaded, extracting data.')

    produtos_elements = driver.find_elements(By.CSS_SELECTOR, 'form[name^="Form"]')
    produtos = []

    for i, produto in enumerate(produtos_elements):
        try:
            produto_indisponivel = produto.find_element(By.CSS_SELECTOR, 'div[id^="zFProdSoldOut"]').text

            if produto_indisponivel == 'Produto indisponível':
                continue

            nome = produto.find_element(By.CLASS_NAME, 'DivProductListNomeProd').text
            preco_bruto = produto.find_element(By.CSS_SELECTOR, 'div[id^="idProdPrice"]').text

            if 'Por' in preco_bruto:
                preco_extraido = re.findall(r'Por R\$ ([0-9,]+)', preco_bruto)[0]

            else:
                preco_extraido = re.findall(r'R\$ ([0-9,]+)', preco_bruto)[0]

            preco_tratado = float(preco_extraido.replace(',', '.'))

            produtos.append([now_str, nome, preco_tratado])

        except NoSuchElementException:
            continue
    
    driver.close()

    return produtos


def scrape_data() -> list:
    page = 1
    max_page = 15
    check_next = True
    data = []

    while check_next:
        try:
            if page >= max_page:
                check_next = False
                continue

            response = requests.get(
                f'https://www.asiashop.com.br/listaprodutos.asp?IDLoja=7773&IDCategoria=56905&xml=1&pag={page}',
                headers=HEADERS,
            )

            if response.status_code != 200:
                print(f'Request error - page {page} - {response.content}')
                check_next = False
                continue

            soup = BeautifulSoup(html.unescape(response.content.decode('latin-1')))
            product_data = soup.find_all('script', type = 'application/ld+json')

            if len(product_data) != 24:
                print(f'Last page: {page}')
                check_next = False

            for product in product_data:
                data.append(json.loads(product.text))

            page += 1

        except Exception as e:
            print(f'Exception - page {page} - {e}')
            page += 1
    
    return data
