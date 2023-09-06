import requests as req
import pandas as pd
import gc
import datetime
import time
import FinanceDataReader as fdr
import traceback
from selenium_stealth import stealth
from bs4 import BeautifulSoup
from marcap import marcap_data
from tqdm import tqdm
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

class dataCollectionCls:
    def discussionNaverData(self, csv_save, codes, start_date, end_date): # 네이버 셀레니움 크롤링
        if csv_save:
            title_code = ''
            headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/116.0.0.0 Safari/537.36'}
            start_date = datetime.datetime.strptime(start_date, '%Y-%m-%d')
            end_date = datetime.datetime.strptime(end_date, '%Y-%m-%d')
            df = pd.DataFrame(columns=range(4))  # 빈 데이터프레임 생성
            df.columns = ['Code', 'Date', 'Title', 'Contents']  # 데이터 프레임 컬럼 지정
            for code in tqdm(codes):
                # 만약 데이터프레임의 길이가 2만 줄 이상이면 csv로 저장하고 df 초기화하기
                if len(df) > 20000:
                    # csv 파일로 저장
                    df.to_csv("./datacollect/naver/output_pd" + str(title_code) + ".csv")

                    # df 초기화
                    df.drop(df.index, inplace=True)

                title_code = code
                # headless 설정
                options = webdriver.ChromeOptions()
                options.add_argument('headless')
                options.add_argument("no-sandbox")
                options.add_argument('window-size=1920x1080')
                options.add_argument("disable-gpu")
                options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92 Safari/537.36")

                # chrome driver
                driver = webdriver.Chrome(options=options)

                # stealth
                stealth(driver,
                        languages=["en-US", "en"],
                        vendor="Google Inc.",
                        platform="Win32",
                        webgl_vendor="Intel Inc.",
                        renderer="Intel Iris OpenGL Engine",
                        fix_hairline=True,
                        )

                # request
                # driver.get(f'https://finance.naver.com/item/board.naver?code={code}') # 페이지를 찾을 수 없습니다.
                driver.get(f'https://finance.naver.com/item/coinfo.naver?code={code}')
                driver.implicitly_wait(20)

                # 종목토론으로 이동 (페이지 요청 찾을 수 없음 -> 해결)
                WebDriverWait(driver, 20).until(EC.presence_of_element_located((By.CSS_SELECTOR, ".tab7"))).click()

                page = 0 # 페이지 카운트
                turn = 0 # 페이지 카운트 시 11번째 이후부터는 '맨앞', '이전'이 생기므로 이를 구분하기 위함
                rep = True # 반복 True
                while rep:
                    try:
                        page += 1

                        # 페이지로 이동
                        test = WebDriverWait(driver, 20).until(EC.presence_of_element_located(
                            (By.CSS_SELECTOR, "table[class='Nnavi'] tbody tr td:nth-child("+str(page)+")")))

                        # 2번째 페이지 부터 앞에 '맨앞'이 생기므로 page+1을 해줌
                        if turn == 1:
                            page += 1

                        # 11번째 페이지 부터 앞에 '맨앞'과 '이전'이 생기므로 page+1을 해줌
                        if test.text == '맨앞' or test.text == '이전':
                            page += 1
                        else :
                            test.click()

                            # 시간, 제목 크롤링
                            dates = WebDriverWait(driver, 20).until(EC.presence_of_all_elements_located(
                                (By.CSS_SELECTOR, "tr[onmouseover='mouseOver(this)'] td:nth-child(1) span")))
                            titles = WebDriverWait(driver, 20).until(EC.presence_of_all_elements_located(
                                (By.CSS_SELECTOR, "td[class='title'] a")))
                            for date, title in zip(dates, titles):
                                dt = datetime.datetime.strptime(date.text.split(' ')[0].replace('.', '-'), '%Y-%m-%d')
                                ti = title.text
                                print(code, dt, ti)
                                
                                # 시작일 조건
                                if start_date < dt:
                                    break

                                # 종료 조건
                                if end_date > dt:
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
                                WebDriverWait(driver, 20).until(EC.presence_of_element_located(
                                    (By.CSS_SELECTOR, "table[class='Nnavi'] tbody tr td:nth-child("+str(page+1)+")"))).click() # 다음 클릭
                                page = 0
                        else:
                            if page == 12 :
                                WebDriverWait(driver, 20).until(EC.presence_of_element_located(
                                    (By.CSS_SELECTOR, "table[class='Nnavi'] tbody tr td:nth-child("+str(page+1)+")"))).click()  # 다음 클릭
                                page = 0

                    except Exception as e:
                        print("에러", "코드 :", str(code), "에러메세지 :", e)
                        print(traceback.format_exc())
                        break

                # driver 해제
                driver.quit()
                gc.collect()

                # 크롤링 정책 상 3초 sleep (종목 넘어갈 때)
                time.sleep(3)

            # csv 파일로 저장
            df.to_csv("./datacollect/naver/output_pd" + str(title_code) + ".csv")

    def discussionDaumData(self, csv_save, codes, start_date, end_date): # 다음 크롤링
        if csv_save:
            title_code = ''
            pages = range(1, 10000)  # 페이지 가져오기
            df = pd.DataFrame(columns=range(7))  # 빈 데이터프레임 생성
            df.columns = ['Code', 'Date', 'Title', 'Contents', 'Readcnt', 'Agreecnt', 'Disagreecnt']  # 데이터 프레임 컬럼 지정
            start_date = datetime.datetime.strptime(start_date, '%Y-%m-%d')
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

                        # 시작일 조건
                        if start_date < createdt:
                            break

                        # 종료일 페이지를 크롤링하면 다음 페이지로 이동
                        if end_date > createdt:
                            break

                        # 데이터프레임에 행 추가
                        df.loc[len(df)] = [code, createdt, title, contents, readcnt, agreecnt, disagreecnt]

                    # 크롤링 정책 상 1초 sleep (페이지 넘어갈 때)
                    time.sleep(1)

                    # 종료일 페이지를 크롤링하면 다음 종목으로 이동
                    if end_date > createdt:
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
            df.to_csv('./datacollect/stockdata/stock.csv')

    def codeData(self): # 종목 코드, 종목명 모두 추출
        today = datetime.datetime.today()
        dayago = today - datetime.timedelta(days=7)
        df = marcap_data(dayago.strftime('%Y-%m-%d'), today.strftime('%Y-%m-%d'))
        df = df.loc[df["Market"] != 'KONEX'] # KONEX 제거
        df = df.loc[df["Market"] != 'KOSPI'] # KOSPI 제거
        df = df.loc[~df.Name.str.contains('([0-9]호)')] # 스팩주 제거
        
        df_code = df[['Code','Name']]
        df_code = df_code.drop_duplicates()
        df_code = df_code.reset_index()
        df_code = df_code.drop('Date', axis=1)
        return df_code

    def indexData(self, csv_save, index='KS11', year='2022'):
        '''
            index : KS11(코스피 지수), KQ11(코스닥 지수), DJI(다우 지수), IXIC(나스닥 지수), US500(S&P5000) [type : str]
            year : '2015' ... [type : str]
        '''
        if csv_save:
            df = fdr.DataReader(index, year) # KS11 (KOSPI 지수), 2015년~현재
            df.to_csv('./datacollect/stockdata/index'+str(index)+'.csv')

    def coinData(self, csv_save, coin='BTC/KRW', year='2022'):
        '''
            coin : BTC/USD(비트코인 달러 가격, 비트파이넥스), BTC/KRW(비트코인 원화 가격, 빗썸) [type : str]
            year : '2015' ... [type : str]
        '''
        if csv_save:
            df = fdr.DataReader(coin, year) # 비트코인 가격
            df.to_csv('./datacollect/stockdata/coin.csv')

    def exchangeRateData(self, csv_save, exchange='USD/KRW', year='2022'):
        '''
             exchange : USD/KRX(원달러 환율), USD/EUR(달러당 유로화 환율), CNY/KRX(위완화 원화 환율) [type : str]
             year : '2015' ... [type : str]
        '''
        if csv_save:
            df = fdr.DataReader(exchange, year) # 원달러 환율
            df.to_csv('./datacollect/stockdata/exchange.csv')

    def themeData(self, csv_save):
        if csv_save:
            url = 'https://finance.naver.com/sise/theme.nhn'
            res = req.get(url)
            soup = BeautifulSoup(res.content, 'html.parser')
            total_pages = int(soup.select_one('.pgRR a')['href'].split('=')[-1])

            theme_list = []
            for page in range(1, total_pages + 1):
                url = f'https://finance.naver.com/sise/theme.nhn?&page={page}'
                res = req.get(url)
                soup = BeautifulSoup(res.content, 'html.parser')
                themes = soup.select('.type_1 .col_type1 a')

                for theme in themes:
                    theme_name = theme.text.strip()
                    theme_url = 'https://finance.naver.com' + theme['href']
                    theme_res = req.get(theme_url)
                    theme_soup = BeautifulSoup(theme_res.content, 'html.parser')
                    stocks = theme_soup.select('.type_5 tbody tr')
                    stock_list = []
                    for stock in stocks:
                        try:
                            stock_name = stock.select_one('a').text.strip()
                            stock_list.append(stock_name)
                        except:
                            pass
                    theme_list.append((theme_name, stock_list))

            # 테마 리스트를 데이터 프레임으로 변환
            df_theme = pd.DataFrame(theme_list, columns=['Theme', 'Name'])
            df_theme.to_csv('datacollect/stockdata/theme_list.csv')