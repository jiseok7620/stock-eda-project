import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from bs4 import BeautifulSoup

codes = ['005930', '010130']
co_lists = ['5', '6']
pages = range(101, 102)

comments = []

driver = webdriver.Chrome()

for code in codes:
    for page in pages:
        url = f'https://finance.naver.com/item/board.naver?code={str(code)}&page={str(page)}'

        for co_list in co_lists:
            driver.get(url)
            time.sleep(1)

            selector = f"tr:nth-child({co_list}) > td.title > a"
            search_button = driver.find_element(By.CSS_SELECTOR, selector)
            search_button.click()
            time.sleep(3)

            html = driver.page_source
            soup = BeautifulSoup(html, 'html.parser')
            comment = soup.select_one('#body')
            comments.append(comment.get_text())

driver.quit()

print(comments)
