import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from bs4 import BeautifulSoup

codes = ['005930']
co_lists = ['3','4']
pages = ['3','4']

coments = []

driver = webdriver.Chrome()
for code in codes:
    for page in pages:
        for co_list in co_lists:
            url = f'https://finance.naver.com/item/board.naver?code={code}&page={page}'
            driver.get(url)
            time.sleep(1)

            selector = f"tr:nth-child({co_list + 1}) > td.title > a"

            
            search_button = driver.find_element(By.CSS_SELECTOR, selector)
            search_button.click()
            time.sleep(3)

            
            html = driver.page_source
            soup = BeautifulSoup(html, 'html.parser')
            
            comment = soup.select_one('#body')
            coments.append(comment.get_text())

driver.quit()

print(coments)
