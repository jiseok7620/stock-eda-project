import requests as req
from bs4 import BeautifulSoup
import re
from datetime import datetime
from marcap import marcap_data

class dataCollectionCls:
    def discussionData(self):
        headers = {'User-Agent' : 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/116.0.0.0 Safari/537.36'}
        urls = 'https://finance.naver.com/item/board.naver?code=373220'
        res = req.get(urls, headers=headers)
        soup = BeautifulSoup(res.text, 'html.parser')

        aa = soup.select("tr[onmouseover='mouseOver(this)'] td:nth-child(1) span")
        bb = soup.find_all(href=re.compile("/item/board_read.naver"))

        for a, b in zip(aa, bb):
            dt = a.contents[0]
            link = b['href']
            title = b['title']

            # 본문의 내용 가져오기
            res2 = req.get('https://finance.naver.com' + link, headers=headers)
            soup2 = BeautifulSoup(res2.text, 'html.parser')
            print(soup2.find(id="body").find_all(text=True))

    def stockData(self):
        today = datetime.today().strftime('%Y-%m-%d')

        # 특정 기간 전종목
        df = marcap_data('2023-01-01', today)  # 2015.06.15부터 상하한가폭 변경
        print(df)
        print(df.columns)
        print(df.head)