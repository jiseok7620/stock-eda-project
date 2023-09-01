import time
import pandas as pd
import re
import matplotlib.pyplot as plt
import numpy as np
from tqdm import tqdm
from konlpy.tag import Twitter

class dataPreprocessingCls:
    def __init__(self):
        self.coin_df = pd.read_csv('./stockdata/coin.csv')
        self.exchange_df = pd.read_csv('./stockdata/exchange.csv')
        self.indexDJI_df = pd.read_csv('./stockdata/indexDJI.csv')
        self.indexIXIC_df = pd.read_csv('./stockdata/indexIXIC.csv')
        self.indexKQ11_df = pd.read_csv('./stockdata/indexKQ11.csv')
        self.indexKS11_df = pd.read_csv('./stockdata/indexKS11.csv')
        self.indexUS500_df = pd.read_csv('./stockdata/indexUS500.csv')
        self.stock_df = pd.read_csv('./stockdata/stock.csv')
        self.daum_df = pd.read_csv('./daum/output.csv', dtype=object)
        self.naver_df = pd.read_csv('./naver/output_pd327260.csv', dtype=object)

    def stockPreprocessing(self, st_date, end_date): # 주식 데이터 전처리
        stock_new = self.stock_df[(self.stock_df['Date'] >= st_date) & (self.stock_df['Date'] <= end_date)] # 주식 한달 데이터 가져오기
        df = pd.merge(stock_new, self.naver_df, how='outer', on=['Code', 'Date']) # 주식 데이터와 종토방 데이터 병합하기
        df = df[~df['Name'].isna()] # 종토방 데이터는 주말데이터가 있으므로 이 데이터는 삭제
        df.to_csv('data.csv')
        for code in df['Code'].unique():
            stock = df[df['Code'] == code]
            print("1. 총 게시글 수")
            print(">>>", len(stock))

            print("2. 요일별 개수")
            days_df = stock.groupby('Date')['Title'].count()  # Date를 기준으로 게시글 수 카운트
            days_df = days_df.to_frame('Num')
            print(days_df)

            print("3. 한달간 댓글 수, 주가")
            stock = stock.drop_duplicates(subset='Date') # Date열 기준 중복제거하기
            stock = stock.set_index('Date', drop=True, append=False) # 컬럼을 인덱스로 지정
            new_df = days_df.join(stock[['High', 'Volume']], how='inner') # 인덱스를 기준으로 합치기

            print("4. 그래프로 그려주기")
            # 정규화 수행
            normalized_df = (new_df - new_df.min()) / (new_df.max() - new_df.min())

            # line 차트 그리기
            plt.figure(figsize=[16,8])
            plt.subplot(2,1,1)
            plt.plot(normalized_df['Num'], label='Num')
            plt.plot(normalized_df['High'], label='Close')
            plt.legend()
            
            # bar 차트 그리기
            plt.subplot(2,1,2)
            plt.bar(new_df.index, new_df['Volume'])
            
            # 차트 보여주기
            plt.show()

    def discussionPreprocessing(self): # 종토방 데이터 전처리
        df = self.daum_df

        for i in range(len(df)):
            # 모든 특수문자, 띄어쓰기
            df.iloc[i]['Title'] = re.sub(r'[^\w가-힣]', '', df.iloc[i]['Title'])
            df.iloc[i]['Contents'] = re.sub(r'[^\w가-힣]', '', df.iloc[i]['Contents'])

        new_df = pd.DataFrame(columns=['Code', 'Date', 'Noun', 'Adjective', 'Verb'])
        twt = Twitter()
        for j in tqdm(range(len(df))):
            tag_a = twt.pos(df.iloc[j]['Title'])
            tag_b = twt.pos(df.iloc[j]['Contents'])
            list_noun = []
            list_ad = []
            list_vb = []
            for a, b in tag_a:
                if b == 'Noun':
                     list_noun.append(a)
                elif b == 'Adjective':
                     list_ad.append(a)
                elif b == 'Verb':
                     list_vb.append(a)
            for a, b in tag_b:
                if b == 'Noun':
                    list_noun.append(a)
                elif b == 'Adjective':
                    list_ad.append(a)
                elif b == 'Verb':
                    list_noun.append(a)
            new_df.loc[len(new_df)] = [df.iloc[j]['Code'], df.iloc[j]['Date'], list_noun, list_ad, list_vb]

        new_df.to_csv('test.csv')
        return new_df

st = dataPreprocessingCls()
st.stockPreprocessing('2023-08-01','2023-08-31')
#st.discussionPreprocessing()
