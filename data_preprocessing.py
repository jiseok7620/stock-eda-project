import os
import pandas as pd
import re
from tqdm import tqdm
from konlpy.tag import Twitter

class dataPreprocessingCls:
    def mergeDiscussion(self, csv_save): # Naver 종목토론방 데이터 합치기
        if csv_save:
            # 폴더 경로 설정
            folder_path = 'datacollect/naver'

            # 모든 CSV 파일을 저장할 빈 DataFrame 생성
            combined_data = pd.DataFrame()

            # 폴더 내의 모든 파일에 대해 반복
            for file_name in os.listdir(folder_path):
                if file_name.endswith('.csv'):  # .csv 확장자인 경우에만 처리
                    file_path = os.path.join(folder_path, file_name)
                    # CSV 파일 읽어오기
                    data = pd.read_csv(file_path)
                    # 읽어온 데이터를 combined_data에 추가하기
                    combined_data = combined_data._append(data)
                    # 인덱스 초기화
                    combined_data = combined_data.reset_index(drop=True)

            # 열 삭제
            combined_data = combined_data.drop(columns='Unnamed: 0')

            # csv로 저장
            combined_data.to_csv('./datapreprocess/combined.csv')

    def stockPreprocessing(self, csv_save, st_date, end_date): # 주식 데이터 + 종목토론방 1개월
        if csv_save:
            stock_df = pd.read_csv('datacollect/stockdata/stock.csv') # 수집한 n일치 주식데이터
            stock_new = stock_df[(stock_df['Date'] >= st_date) & (stock_df['Date'] <= end_date)] # 주식 한달 데이터 가져오기
            stock_new = stock_new.reset_index(drop=True)
            # print("\n\n>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>")
            # print(stock_new)
            # print(stock_new.info())
            # print(len(stock_new.drop_duplicates(subset=['Code'])))

            in_df = pd.read_csv('datapreprocess/combined.csv', dtype=object) # 수집한 한달 네이버 종토방 데이터(합친거)
            in_df = in_df.drop(columns='Unnamed: 0')
            in_df.Code = in_df.Code.apply(lambda x: x.zfill(6))
            # print("\n\n>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>")
            # print(in_df)
            # print(in_df.info())
            # print(len(in_df.drop_duplicates(subset=['Code'])))

            df = pd.merge(stock_new, in_df, how='outer', on=['Code', 'Date']) # 주식 데이터와 종토방 데이터 병합하기
            # print("\n\n>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>")
            # print(df)
            # print(df.info())
            # print(len(df.drop_duplicates(subset=['Code'])))

            df = df[~df['Name'].isna()] # 종토방 데이터는 주말데이터가 있으므로 이 데이터는 삭제
            # print("\n\n>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>")
            # print(df)
            # print(df.info())
            # print(len(df.drop_duplicates(subset=['Code'])))

            result_df = pd.DataFrame()
            for code in tqdm(in_df['Code'].unique()):
                stock = df[df['Code'] == code]
                # if len(stock[~stock['Title'].isna()]) == 0 :
                #     continue
                # else :
                # 요일별 개수
                days_df = stock.groupby('Date')['Title'].count() # Date를 기준으로 게시글 수 카운트
                days_df = days_df.to_frame('Num')

                # 한달간 댓글 수, 주가
                stock = stock.drop_duplicates(subset='Date') # Date열 기준 중복제거하기
                stock = stock.set_index('Date', drop=True, append=False) # 컬럼을 인덱스로 지정
                new_df = days_df.join(stock[['Code', 'Open', 'High', 'Low', 'Close', 'Volume']], how='inner') # 인덱스를 기준으로 합치기
                new_df = new_df.reset_index() # Date 인덱스를 컬럼으로 변경
                result_df = result_df._append(new_df)
                result_df = result_df.reset_index(drop=True) # 0~ 인덱스 중복을 초기화

            # csv로 저장
            result_df.to_csv('./datapreprocess/discussionnum.csv')

    def discussionPreprocessing(self, csv_save): # 종토방 데이터 전처리
        if csv_save:
            df = pd.read_csv('datapreprocess/combined.csv', dtype=object)
            df[['Title', 'Contents']] = df[['Title', 'Contents']].astype(dtype='str')
            df = df.astype({'Code': 'str'})
            df['Code'] = df['Code'].apply(lambda x: x.zfill(6))

            # 상위 1개, 하위 1개 종목만 추출
            df = df.loc[(df['Code'] == '250000') | (df['Code'] == '053030')]
            print(df['Code'].unique())

            title_values = df['Title'].str.findall(r"[ㄱ-ㅎ가-힣0-9]+")
            content_values = df['Contents'].str.findall(r"[ㄱ-ㅎ가-힣0-9]+")
            title_result = title_values.str.join('')
            content_result = content_values.str.join('')
            df['Title'] = title_result
            df['Contents'] = content_result

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
        theme_list = pd.read_csv('datacollect/stockdata/theme_list.csv')
        theme_list = theme_list.iloc[:, 1:]
        for theme_name, stock_list in zip(theme_list.Theme, theme_list.Name):
            if theme_name == theme_name_input:
                return stock_list
        return None

    def getThemesByStock(self, stock_name_input): # 종목이 속한 테마들
        theme_list = pd.read_csv('datacollect/stockdata/theme_list.csv')
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
