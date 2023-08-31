import bs4
import requests as req
import pandas as pd
import re
import datetime
import time
import FinanceDataReader as fdr
from io import BytesIO
from bs4 import BeautifulSoup
from marcap import marcap_data
from tqdm import tqdm
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


class dataCollectionCls:
    def discussionData(self, csv_save, codes, end_date): # 네이버 bf 크롤링 - request 문제 발생(100page 이후 크롤링 불가능)
        if csv_save:
            headers = {'User-Agent' : 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/116.0.0.0 Safari/537.36'}

            title_code = ''
            pages = range(1, 3) # 페이지 가져오기
            codes = codes[1001:1005] # 종목 추출(네이버 크롤링 보안정책상)
            df = pd.DataFrame(columns=range(4))  # 빈 데이터프레임 생성
            df.columns = ['Code', 'Date', 'Title', 'Contents']  # 데이터 프레임 컬럼 지정
            end_date = datetime.datetime.strptime(end_date, '%Y-%m-%d')
            for code in tqdm(codes):
                title_code = code
                for page in pages:
                    urls = f'https://finance.naver.com/item/board.naver?code={str(code)}&page={str(page)}'
                    res = req.get(urls, headers=headers)
                    soup = BeautifulSoup(res.text, 'html.parser')

                    aa = soup.select("tr[onmouseover='mouseOver(this)'] td:nth-child(1) span") # 시간을 가져오기 위함
                    bb = soup.find_all(href=re.compile("/item/board_read.naver")) # 제목을 가져옴

                    for a, b in zip(aa, bb):
                        dt = datetime.datetime.strptime(a.contents[0].split(' ')[0].replace('.','-'), '%Y-%m-%d')
                        link = b['href']
                        title = b['title']
                        print(code, page, dt)

                        # 종료일 페이지를 크롤링하면 다음 페이지로 이동
                        if end_date >= dt:
                            break

                        # 본문의 내용 가져오기
                        res2 = req.get('https://finance.naver.com' + link, headers=headers)
                        soup2 = BeautifulSoup(res2.text, 'html.parser')

                        # 데이터프레임에 행 추가
                        df.loc[len(df)] = [code, dt, title, soup2.find(id="body").find_all(text=True)]

                        # 네이버 크롤링 정책 상 0.5초 sleep (본문 넘어갈 때)
                        time.sleep(0.5)

                    # 네이버 크롤링 정책 상 1초 sleep (페이지 넘어갈 때)
                    time.sleep(1)

                    # 종료일 페이지를 크롤링하면 다음 종목으로 이동
                    if end_date >= dt:
                        break

                # 네이버 크롤링 정책 상 5초 sleep (종목코드 넘어갈 때)
                time.sleep(5)

            # csv 파일로 저장
            df.to_csv("./output/output_pd"+str(title_code)+".csv")

    def discussionNaverData(self, csv_save, codes, end_date): # 네이버 셀레니움 크롤링
        if csv_save:
            title_code = ''
            headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/116.0.0.0 Safari/537.36'}
            end_date = datetime.datetime.strptime(end_date, '%Y-%m-%d')
            df = pd.DataFrame(columns=range(4))  # 빈 데이터프레임 생성
            df.columns = ['Code', 'Date', 'Title', 'Contents']  # 데이터 프레임 컬럼 지정
            for code in tqdm(codes):
                title_code = code
                # headless 설정
                options = webdriver.ChromeOptions()
                options.add_argument('headless')
                options.add_argument("no-sandbox")
                options.add_argument('window-size=1920x1080')
                options.add_argument("disable-gpu")
                options.add_argument("user-agent=Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/61.0.3163.100 Safari/537.36")

                # chrome driver
                driver = webdriver.Chrome(options=options)
                driver.get(f'https://finance.naver.com/item/board.naver?code={code}')
                driver.implicitly_wait(5)

                page = 0 # 페이지 카운트
                turn = 0 # 페이지 카운트 시 11번째 이후부터는 '맨앞', '이전'이 생기므로 이를 구분하기 위함
                rep = True # 반복 True
                while rep:
                    try:
                        page += 1

                        # 페이지로 이동
                        test = driver.find_element(By.CSS_SELECTOR, "table[class='Nnavi'] tbody tr td:nth-child("+str(page)+")")
                        driver.implicitly_wait(5)

                        # 2번째 페이지 부터 앞에 '맨앞'이 생기므로 page+1을 해줌
                        if turn == 1:
                            page += 1

                        # 11번째 페이지 부터 앞에 '맨앞'과 '이전'이 생기므로 page+1을 해줌
                        if test.text == '맨앞' or test.text == '이전':
                            page += 1
                        else :
                            test.click()

                            # 시간, 제목 크롤링
                            dates = driver.find_elements(By.CSS_SELECTOR, "tr[onmouseover='mouseOver(this)'] td:nth-child(1) span")
                            titles = driver.find_elements(By.CSS_SELECTOR, "td[class='title'] a")
                            for date, title in zip(dates, titles):
                                dt = datetime.datetime.strptime(date.text.split(' ')[0].replace('.', '-'), '%Y-%m-%d')
                                ti = title.text

                                # 종료 조건
                                if end_date >= dt:
                                    rep = False
                                    break

                                # 본문의 내용 가져오기
                                res = req.get(title.get_attribute('href'), headers=headers)
                                soup = BeautifulSoup(res.text, 'html.parser')
                                content = soup.find(id="body").find_all(text=True)

                                # 데이터프레임에 행 추가
                                df.loc[len(df)] = [code, dt, ti, content]

                                # 크롤링 정책 상 0.2초 sleep (본문 넘어갈 때)
                                time.sleep(0.2)

                        # turn + 1
                        turn += 1

                        # turn이 10은 첫 번째 턴(맨앞 버튼만), 이후는 맨앞, 이전 버튼
                        if turn == 10:
                            if page == 11 :
                                driver.find_element(By.CSS_SELECTOR, "table[class='Nnavi'] tbody tr td:nth-child("+str(page+1)+")").click() # 다음 클릭
                                page = 0
                        else:
                            if page == 12 :
                                driver.find_element(By.CSS_SELECTOR, "table[class='Nnavi'] tbody tr td:nth-child("+str(page+1)+")").click() # 다음 클릭
                                page = 0

                    except Exception as e:
                        print("에러", "코드 :", str(code), "에러메세지 :", e)
                        break

                # driver 해제
                driver.quit()

                # 크롤링 정책 상 3초 sleep (종목 넘어갈 때)
                time.sleep(3)

            # csv 파일로 저장
            df.to_csv("./naver/output_pd" + str(title_code) + ".csv")

    def discussionDaumData(self, csv_save, codes, end_date): # 다음 크롤링
        if csv_save:
            title_code = ''
            pages = range(1, 10000)  # 페이지 가져오기
            df = pd.DataFrame(columns=range(7))  # 빈 데이터프레임 생성
            df.columns = ['Code', 'Date', 'Title', 'Contents', 'Readcnt', 'Agreecnt', 'Disagreecnt']  # 데이터 프레임 컬럼 지정
            end_date = datetime.datetime.strptime(end_date, '%Y-%m-%d')
            for code in tqdm(codes):
                title_code = code
                for page in pages:
                    url = f'https://finance.daum.net/content/debates/A{code}?symbolCode=A{code}&page={page}&perPage=100&notice=true&pagination=true'

                    headers = {
                        'Referer': 'http://finance.daum.net',
                        'User-Agent': 'Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/71.0.3578.98 Safari/537.36 OPR/58.0.3135.127'
                    }

                    res = req.get(url, headers=headers)
                    json_data = res.json()

                    # 가져오는 기사 개수가 30개 이하이면 다음 종목으로 넘어가기
                    if json_data['totalCount'] <= 30 :
                        break

                    for js in json_data['data']['posts']:
                        createdt = datetime.datetime.strptime(js['createdAt'].split(' ')[0], '%Y-%m-%d')
                        title = js['title']
                        contents = js['content']
                        readcnt = js['readCount']
                        agreecnt = js['agreeCount']
                        disagreecnt = js['disagreeCount']
                        #print(code, end_date, createdt, title)

                        # 종료일 페이지를 크롤링하면 다음 페이지로 이동
                        if end_date >= createdt:
                            break

                        # 데이터프레임에 행 추가
                        df.loc[len(df)] = [code, createdt, title, contents, readcnt, agreecnt, disagreecnt]

                    # 크롤링 정책 상 1초 sleep (페이지 넘어갈 때)
                    time.sleep(1)

                    # 종료일 페이지를 크롤링하면 다음 종목으로 이동
                    if end_date >= createdt:
                        break

                # 크롤링 정책 상 3초 sleep (종목 넘어갈 때)
                time.sleep(3)

            # csv 파일로 저장
            df.to_csv("./daum/output_pd" + str(title_code) + ".csv")

    def stockData(self, csv_save, stday): # 주식 데이터 가져오기
        if csv_save:
            today = datetime.datetime.today().strftime('%Y-%m-%d')
    
            # fdr로 전체 종목 가져오기 (섹터 데이터)
            krx_df = fdr.StockListing('KRX')
            # marcap으로 전 종목 데이터 가져오기 (시간 형식 : %Y-%m-%d) / 2015.06.15부터 상하한가폭 변경
            df = marcap_data(stday, today)
            df = df.loc[df["Market"] != 'KONEX']  # KONEX 제거
            df = df.loc[df["Market"] != 'KOSPI']  # KOSPI 제거
            df = df.loc[~df.Name.str.contains('([0-9]호)')]  # 스팩주 제거
            
            # csv로 저장
            krx_df.to_csv('./stockdata/sector.csv')
            df.to_csv('./stockdata/stock.csv')

    def codeData(self): # 종목 코드 모두 추출
        today = datetime.datetime.today()
        dayago = today - datetime.timedelta(days=7)
        df = marcap_data(dayago.strftime('%Y-%m-%d'), today.strftime('%Y-%m-%d'))
        df = df.loc[df["Market"] != 'KONEX'] # KONEX 제거
        df = df.loc[df["Market"] != 'KOSPI'] # KOSPI 제거
        df = df.loc[~df.Name.str.contains('([0-9]호)')] # 스팩주 제거

        arr_code = df.Code.unique() # <class 'numpy.ndarray'>
        return arr_code

    def indexData(self, csv_save, index='KS11', year='2022'):
        '''
            index : KS11(코스피 지수), KQ11(코스닥 지수), DJI(다우 지수), IXIC(나스닥 지수), US500(S&P5000) [type : str]
            year : '2015' ... [type : str]
        '''
        if csv_save:
            df = fdr.DataReader(index, year) # KS11 (KOSPI 지수), 2015년~현재
            df.to_csv('./stockdata/index'+str(index)+'.csv')

    def coinData(self, csv_save, coin='BTC/KRW', year='2022'):
        '''
            coin : BTC/USD(비트코인 달러 가격, 비트파이넥스), BTC/KRW(비트코인 원화 가격, 빗썸) [type : str]
            year : '2015' ... [type : str]
        '''
        if csv_save:
            df = fdr.DataReader(coin, year) # 비트코인 가격
            df.to_csv('./stockdata/coin.csv')

    def exchangeRateData(self, csv_save, exchange='USD/KRW', year='2022'):
        '''
             exchange : USD/KRX(원달러 환율), USD/EUR(달러당 유로화 환율), CNY/KRX(위완화 원화 환율) [type : str]
             year : '2015' ... [type : str]
        '''
        if csv_save:
            df = fdr.DataReader(exchange, year) # 원달러 환율
            df.to_csv('./stockdata/exchange.csv')

    def listingData(self):
        gen_req_url = 'http://data.krx.co.kr/comm/fileDn/GenerateOTP/generate.cmd'
        query_str_parms = {
            'mktId': 'ALL',
            'share': '1',
            'csvxls_isNo': 'false',
            'name': 'fileDown',
            'url': 'dbms/MDC/STAT/standard/MDCSTAT01901'
        }
        headers = {
            'Referer': 'http://data.krx.co.kr/contents/MDC/MDI/mdiLoader/index.cmd?menuId=MDC0302_DB',
            'Upgrade-Insecure-Requests': '1',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/111.0.0.0 Safari/537.36'
            # generate.cmd에서 찾아서 입력하세요
        }
        res1 = req.get(gen_req_url, query_str_parms, headers=headers)
        gen_req_url = 'http://data.krx.co.kr/comm/fileDn/download_excel/download.cmd'
        form_data = {
            'code': res1.content
        }
        res2 = req.post(gen_req_url, form_data, headers=headers)
        csv_file = BytesIO(res2.content)
        df = pd.read_csv(csv_file, encoding='euc-kr')
