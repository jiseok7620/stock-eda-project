import time
import pandas as pd
import re
from tqdm import tqdm
from konlpy.tag import Twitter

class dataPreprocessingCls:
    def __init__(self):
        self.coin_df = pd.read_csv('datacollect/stockdata/coin.csv')
        self.exchange_df = pd.read_csv('datacollect/stockdata/exchange.csv')
        self.indexDJI_df = pd.read_csv('datacollect/stockdata/indexDJI.csv')
        self.indexIXIC_df = pd.read_csv('datacollect/stockdata/indexIXIC.csv')
        self.indexKQ11_df = pd.read_csv('datacollect/stockdata/indexKQ11.csv')
        self.indexKS11_df = pd.read_csv('datacollect/stockdata/indexKS11.csv')
        self.indexUS500_df = pd.read_csv('datacollect/stockdata/indexUS500.csv')
        self.theme_df = pd.read_csv('datacollect/stockdata/theme_list.csv')
        self.stock_df = pd.read_csv('datacollect/stockdata/stock.csv')
        self.daum_df = pd.read_csv('datacollect/daum/output.csv', dtype=object)
        self.naver_df = pd.read_csv('datacollect/naver/output_pd327260.csv', dtype=object)

    def mergeDiscussion(self): # Naver 종목토론방 데이터 합치기
        pass

    def stockPreprocessing(self, csv_save, in_df, st_date, end_date): # 주식 데이터 + 종목토론방 1개월
        if csv_save:
            stock_new = self.stock_df[(self.stock_df['Date'] >= st_date) & (self.stock_df['Date'] <= end_date)] # 주식 한달 데이터 가져오기
            df = pd.merge(stock_new, in_df, how='outer', on=['Code', 'Date']) # 주식 데이터와 종토방 데이터 병합하기
            df = df[~df['Name'].isna()] # 종토방 데이터는 주말데이터가 있으므로 이 데이터는 삭제
            result_df = pd.DataFrame()
            for code in tqdm(df['Code'].unique()):
                stock = df[df['Code'] == code]
                if len(stock[~stock['Title'].isna()]) == 0 :
                    continue
                else :
                    # 요일별 개수
                    days_df = stock.groupby('Date')['Title'].count() # Date를 기준으로 게시글 수 카운트
                    days_df = days_df.to_frame('Num')

                    # 한달간 댓글 수, 주가
                    stock = stock.drop_duplicates(subset='Date') # Date열 기준 중복제거하기
                    stock = stock.set_index('Date', drop=True, append=False) # 컬럼을 인덱스로 지정
                    new_df = days_df.join(stock[['Code', 'Close', 'Volume']], how='inner') # 인덱스를 기준으로 합치기
                    new_df = new_df.reset_index() # Date 인덱스를 컬럼으로 변경
                    result_df = result_df._append(new_df)
                    result_df = result_df.reset_index(drop=True) # 0~ 인덱스 중복을 초기화

            # csv로 저장
            result_df.to_csv('./datapreprocess/discussionnum.csv')

    def discussionPreprocessing(self, csv_save, df): # 종토방 데이터 전처리
        if csv_save:
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

            # csv로 저장
            new_df.to_csv('./datapreprocess/morpheme.csv')

    def getStocksByTheme(self, theme_name_input): # 테마에 속한 종목들
        theme_list = self.theme_df
        theme_list = theme_list.iloc[:, 1:]
        for theme_name, stock_list in zip(theme_list.Theme, theme_list.Name):
            if theme_name == theme_name_input:
                return stock_list
        return None

    def getThemesByStock(self, stock_name_input): # 종목이 속한 테마들
        theme_list = self.theme_df
        theme_list = theme_list.iloc[:, 1:]
        themes = []
        for theme_name, stock_list in zip(theme_list.Theme, theme_list.Name):
            if stock_name_input in stock_list:
                themes.append(theme_name)
        return themes

    def getThemeData(self, csv_save, df): # 테마열 추가하기
        if csv_save:
            result_df = df
            result_df['Theme'] = ''
            for index, name_input in df.iterrows():
                themes = self.getThemesByStock(name_input.Name)
                theme_list = []

                if len(themes) == 0:
                    continue
                else:
                    for theme_name in themes:
                        theme_list.append(theme_name)
                result_df.at[index, 'Theme'] = theme_list # 리스트를 특정 요소에 할당하기

            # csv로 저장
            result_df.to_csv('./datapreprocess/stocktheme.csv')
