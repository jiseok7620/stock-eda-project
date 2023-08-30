import pandas as pd
import numpy as np
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
        self.discuss_df = pd.read_csv('./output/output_pd950160.csv', dtype=object)

    def stockPreprocessing(self): # 주식 데이터 전처리
        pass

    def discussionPreprocessing(self): # 주식 + 종토방 데이터 전처리
        df = self.discuss_df.copy()
        df = df[['Title','Contents']]
        twt = Twitter()

        '''
        for i in df['Title']:
            tagging = twt.pos(i)
            print(tagging)
        '''

        for i in df['Contents']:
            tagging = twt.pos(i)
            print(tagging)

        #df = pd.merge(self.stock_df, self.discuss_df, how='inner', on=['Code', 'Date'])
        #print(df)

'''
st = dataPreprocessingCls()
st.discussionPreprocessing()
'''