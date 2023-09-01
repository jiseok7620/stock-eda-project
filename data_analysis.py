import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import json
from wordcloud import WordCloud

class dataAnalysisCls:
    def data_list(self, wordname): # SentiWord_info의 json 사전의 긍정/부정/중립 값의 Score 가져오기
        with open('data/SentiWord_info.json', encoding='utf-8-sig', mode='r') as f:
            data = json.load(f)

        result = 9999
        result2 = 'None'
        for i in range(0, len(data)):
            if wordname in data[i]['word']:
                result = data[i]['polarity']
                result2 = data[i]['word']

        return result, result2

    def discussAnalysis(self, df): # 감성분석 1) 긍정, 부정, 중립 점수 매기기
        for li in df['Verb'].astype('object'):
            noun_list = []
            text = li.replace('[', '').replace(']', '').replace('\'', '').replace(' ', '')
            text_li = text.split(',')
            for i in text_li:
                result, result2 = self.data_list(i)
                noun_list.append([result, i, result2])
            print(noun_list)

    def commentsAnalysis(self, new_df): # 토론방 게시글 수와 주가의 관계 분석
        # 정규화 수행
        normalized_df = (new_df - new_df.min()) / (new_df.max() - new_df.min())

        # line 차트 그리기
        plt.figure(figsize=[16, 8])
        plt.subplot(2, 1, 1)
        plt.plot(normalized_df['Num'], label='Num')
        plt.plot(normalized_df['High'], label='Close')
        plt.legend()

        # bar 차트 그리기
        plt.subplot(2, 1, 2)
        plt.bar(new_df.index, new_df['Volume'])

        # 차트 보여주기
        plt.show()


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