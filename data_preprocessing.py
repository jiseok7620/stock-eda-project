import pandas as pd
import re
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

    def stockPreprocessing(self): # 주식 데이터 전처리
        pass

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

#st = dataPreprocessingCls()
#st.discussionPreprocessing()
