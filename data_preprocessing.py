import pandas as pd
import re
import json
import numpy as np
from konlpy.tag import Twitter
from wordcloud import WordCloud

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

    def data_list(self, wordname):
        with open('data/SentiWord_info.json', encoding='utf-8-sig', mode='r') as f:
            data = json.load(f)

        result = ['None', 'None']
        for i in range(0, len(data)):
            if data[i]['word'] == wordname:
                result.pop()
                result.pop()
                result.append(data[i]['word_root'])
                result.append(data[i]['polarity'])

        r_word = result[0]
        s_word = result[1]

        print('어근 : ' + r_word)
        print('극성 : ' + s_word)

    def stockPreprocessing(self): # 주식 데이터 전처리
        pass

    def discussionPreprocessing(self): # 주식 + 종토방 데이터 전처리
        df = self.daum_df.copy()
        df = df[['Title','Contents']]

        '''
        # 형태소 분석
        twt = Twitter()
        sy = []
        for i in df['Contents']:
            tagging = twt.pos(i)
            for i, j in tagging:
                # '동사', '명사'만 추출
                if j == 'Noun' or j == 'Verb':
                    sy.append(i)
        print(sy)
        '''

        # 문자열 분석
        for content in df['Contents']:
            # '%'를 제외한 모든 특수문자를 제거
            result = re.sub(r'[^\w\s%]', '', content)
            # 영어 알파벳을 제거
            result = re.sub(r'[a-zA-Z]', '', result)
            print(result)

        #df = pd.merge(self.stock_df, self.discuss_df, how='inner', on=['Code', 'Date'])
        #print(df)

st = dataPreprocessingCls()
#st.discussionPreprocessing()
st.data_list('가년스럽다')
