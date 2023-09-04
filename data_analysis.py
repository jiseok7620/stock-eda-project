import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import json
import seaborn as sns
from wordcloud import WordCloud

class dataAnalysisCls:
    def __init__(self):
        self.num_df = pd.read_csv('datapreprocess/discussionnum.csv')
        self.morpheme_df = pd.read_csv('datapreprocess/morpheme.csv')
        self.theme_df = pd.read_csv('datapreprocess/stocktheme.csv')
        self.test_df = pd.read_csv('datacollect/daum/output.csv')

    def data_list(self, wordname): # SentiWord_info의 json 사전의 긍정/부정/중립 값의 Score 가져오기
        with open('data/SentiWord_info.json', encoding='utf-8-sig', mode='r') as f:
            data = json.load(f)

        result = 9999
        result2 = 'None'
        for i in range(0, len(data)):
            #if wordname in data[i]['word']: # 형태소 1
                #result = data[i]['polarity']
                #result2 = data[i]['word']
            #if wordname == data[i]['word'][0:len(wordname)]: # 형태소 2
                #result = data[i]['polarity']
                #result2 = data[i]['word']
            if data[i]['word'] in wordname:
                result = data[i]['polarity']
                result2 = data[i]['word']

        return result, result2

    def discussAnalysis(self, df): # 감성분석 1) 긍정, 부정, 중립 점수 매기기 (df : morpheme.csv) : 1) 형태소
        for li in df['Noun'].astype('object'): # Noun, Adjective, Verb
            noun_list = []
            text = li.replace('[', '').replace(']', '').replace('\'', '').replace(' ', '')
            text_li = text.split(',')
            if len(text_li) <= 1: # 내용이 없으면 넘어가기
                continue
            for i in text_li:
                if len(i) <= 1: # 추출한 형태소 길이가 1이하면 넘어가기
                    continue
                result, result2 = self.data_list(i)
                noun_list.append([result, i, result2])
            print(noun_list)

    def discussAnalysis2(self, df): # 감성분석 1) 긍정, 부정, 중립 점수 매기기 (df : morpheme.csv) : 2) 문장
        for text in df['title'].astype('object'): # Noun, Adjective, Verb
            noun_list = []
            result, result2 = self.data_list(text)
            noun_list.append([result, text[0:10], result2])
            print(noun_list)

    def commentsAnalysis(self, df): # 토론방 게시글 수와 주가의 관계 분석 (new_df : discussionnum)
        # 정규화 수행
        df[['Num', 'Close']] = (df[['Num', 'Close']] - df[['Num', 'Close']].min()) / (df[['Num', 'Close']].max() - df[['Num', 'Close']].min()) # Num, Close

        for i in df['Code'].unique():
            graph_df = df[df['Code'] == i]

            # line 차트 그리기
            plt.figure(figsize=[16, 8])
            plt.subplot(2, 1, 1)
            plt.plot(graph_df['Date'], graph_df['Num'], 'bo', label='Num', linestyle='--', marker='*')
            plt.plot(graph_df['Date'], graph_df['Close'], 'bo', label='Close', linestyle='-', color='red')
            plt.legend()

            # bar 차트 그리기
            plt.subplot(2, 1, 2)
            plt.bar(graph_df['Date'], graph_df['Volume'])

            # 차트 보여주기
            plt.show()

            break

    def barGraph(self):
        '''
        1) 범주화 그래프 = x축 : 게시글 수 범위, y축 : 종목 수
        2) boxplot = 변수 : 월별 게시글 수의 합 (outlier 보기)
        '''
        df = self.num_df

        # 종목 코드 별로 그룹화하여 게시글 수의 합 구하기
        gr = df.groupby('Code').sum()
        ne = gr['Num']

        # 범주화하기
        list = [0, ne.max()/4, ne.max()/3, ne.max()/2, ne.max()]
        labels = [str(int(ne.max()/4)), str(int(ne.max()/3)), str(int(ne.max()/2)), str(int(ne.max()))]
        new_sr = pd.cut(ne, list, labels=labels)

        # 범주별로 종목의 개수 count하기
        new_sr = new_sr.value_counts()
        new_sr = new_sr.sort_index()

        # 그래프 한글 깨짐 방지
        plt.rc('font', family='NanumGothic')

        # barplot 생성 (Matplotlib의 bar)
        plt.plot(new_sr.index, new_sr.values, 'ro', linestyle='-')

        # 축 및 제목 설정
        plt.xlabel('게시글 분류')
        plt.ylabel('종목 수')
        plt.title('범주화 그래프')
        #plt.show()

        # 1. 왜도, 첨도

        # boxplot 그리기
        sns.set(style="darkgrid")
        ax = sns.boxplot(y=ne.values)
        sns.swarmplot(y=ne.values, color="grey")
        #plt.show()

        # 2. outlier 리스트 뽑기
        q1 = ne.quantile(0.25)
        q3 = ne.quantile(0.75)
        iqr = q3 - q1
        outliers = ne[ne > q3+1.5*iqr]
        outliers = outliers.reset_index()  # 0~ 인덱스 중복을 초기화
        outliers = outliers.astype({'Code' : 'str'})
        outliers.Code = outliers['Code'].apply(lambda x: x.zfill(6)) #outliers.Code = outliers['Code'].apply(lambda x: str(0) + x if len(x) <= 5 else x)

        # 3. 테마 열 추가하기
        theme_df = self.theme_df.merge(outliers, how='inner', on='Code')
        theme_df = theme_df.iloc[:,1:5]

        # 4. pie chart 그리기


    def leadAnalysis(self): # 주도주 찾기
        pass

    def soarAnalysis(self): # 급등주 찾기
        pass

    def indexCompareAnalysis(self): # 지수와 주가와 상관관계 분석 -> 당연히 상관관계가 클텐데 이상치를 찾아 분석하기
        pass

    def DOWAnalysis(self): # 요일(Day of week)과 주가의 상관관계 분석
        pass

    def sectorAnalysis(self): # 주식 섹터별 가장 많이오른 섹터 찾기 -> 섹터 구분 찾으면..
        pass

    def usaAnalysis(self): # 미국 지수와 한국 지수의 상관관계 분석
        pass

    def coinAnalysis(self): # 코인과 주가의 상관관계 분석
        pass

    def exchangeRateAnalysis(self): # 환율과 주가의 상관관계 분석
        pass

    # 거시경제지표랑 비교 (나중..)