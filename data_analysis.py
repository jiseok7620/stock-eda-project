import pandas as pd
import numpy as np
from mplfinance.original_flavor import candlestick2_ohlc
import matplotlib.gridspec as gridspec
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

    def outlierAnalysis(self): # 게시글 수의 아웃라이어 분석
        df = self.num_df

        # 종목 코드 별로 그룹화하여 게시글 수의 합 구하기
        gr = df.groupby('Code').sum()
        ne = gr['Num']

        # 2. outlier 리스트 뽑기
        q1 = ne.quantile(0.25)
        q3 = ne.quantile(0.75)
        iqr = q3 - q1
        outliers = ne[ne > q3 + 1.5 * iqr]
        outliers = outliers.reset_index()  # 0~ 인덱스 중복을 초기화
        outliers = outliers.astype({'Code': 'str'})
        outliers.Code = outliers['Code'].apply(
            lambda x: x.zfill(6))  # outliers.Code = outliers['Code'].apply(lambda x: str(0) + x if len(x) <= 5 else x)

        return outliers

    def commentsAnalysis(self, outlier_df): # 토론방 게시글 수와 주가의 관계 분석 (num_df : discussionnum)
        df = self.num_df
        df['Code'] = df['Code'].astype(str)  # Code 열을 str로 타입 변환
        df.Code = df['Code'].apply(lambda x: x.zfill(6))  # Code 열의 앞을 0으로 채우기

        # 상관계수가 높은 종목들 추출
        corr_df = pd.DataFrame(columns=['Code', 'Corr'])
        for i in outlier_df['Code'].unique():
            graph_df = df[df['Code'] == i]
            corr_val = graph_df['Num'].corr(df['Close'])
            corr_df.loc[len(corr_df)] = [str(i).zfill(6), corr_val]
        corr_df = corr_df.sort_values(by=['Corr'], ascending=False)
        corr_df = corr_df.reset_index(drop=True)

        return corr_df

    def commentsGraph(self, corr_df):
        df = self.num_df

        # 상관계수가 높은 상위 5개 종목을 그래프로 표현하기
        for i in corr_df.loc[0:4, 'Code']:
            graph_df = df[df['Code'] == i]
            graph_df = graph_df.reset_index(drop=True)  # 인덱스 리셋하기

            # 차트 설정
            plt.figure(figsize=(16, 8))
            plt.rc('font', family='NanumGothic')  # 그래프 한글 깨짐 방지
            gs = gridspec.GridSpec(nrows=2, ncols=1, height_ratios=[3, 1])

            # 트위차트(1) - 봉 차트
            ax = plt.subplot(gs[0])
            ax.set_ylabel('주가', color='black')
            candlestick2_ohlc(ax, graph_df['Open'], graph_df['High'], graph_df['Low'], graph_df['Close'], width=0.5,
                              colorup='r', colordown='b')
            ax.get_xaxis().set_visible(False)

            # 트윈차트(2) - 게시글 수 차트
            ax1 = ax.twinx()
            ax1.set_ylabel('게시글 수', color='black')
            ax1.plot(graph_df['Date'], graph_df['Num'], 'go', linestyle='--', label='게시글수')
            ax1.legend(loc='upper right')

            # 거래량 차트
            ax2 = plt.subplot(gs[1])
            ax2.bar(graph_df['Date'], graph_df['Volume'], color='k', label='거래량')
            ax2.legend(loc='upper right')

            # 차트 그리기
            plt.xlabel('날짜', color='black')
            plt.xticks(rotation=45)  # x-축 글씨 45도 회전
            plt.show()

    def scatterGraph(self, outlier_df):
        df = self.num_df

        # 평균 거래량, 평균 종가
        result_df = pd.DataFrame(columns=['Code','A','B'])
        for i in outlier_df['Code']:
            graph_df = df[df['Code'] == i]
            rate = [round(((a - b) / b) * 100, 2) for a, b in zip(graph_df.Close[1:len(graph_df) - 1], graph_df.Close[0:len(graph_df)])]
            print(graph_df)
            print(rate)

            vol_mean = graph_df.Volume.mean()
            stock_mean = graph_df.Close.mean()
            result_df.loc[len(result_df)] = [i, vol_mean, stock_mean]
            return
        # Add a column: the color depends on x and y values, but you can use any function you want
        # value = (df['x'] > 0.2) & (df['y'] > 0.4)
        # df['color'] = np.where(value == True, "#9b59b6", "#3498db")

        # plot
        sns.regplot(data=result_df, x="A", y="B", fit_reg=False)#, scatter_kws={'facecolors': df['color']})

        plt.show()

    def heatmapGraph(self, corr_df):
        df = self.num_df

        # 8월 한달 데이터가져오기(상관관계 : 코스피지수, 코스닥지수, 환율, 등등)
        st_date = '2023-08-01'
        ed_date = '2023-08-31'
        ks_df = pd.read_csv('datacollect/stockdata/indexKS11.csv')
        kq_df = pd.read_csv('datacollect/stockdata/indexKQ11.csv')
        ec_df = pd.read_csv('datacollect/stockdata/exchange.csv')
        ks_df = ks_df[(ks_df['Date'] <= ed_date) & (ks_df['Date'] >= st_date)]
        ks_df = ks_df.reset_index(drop=True)
        ks_df = ks_df.rename(columns={'Close' : 'Close_ks'})
        kq_df = kq_df[(kq_df['Date'] <= ed_date) & (kq_df['Date'] >= st_date)]
        kq_df = kq_df.reset_index(drop=True)
        kq_df = kq_df.rename(columns={'Close': 'Close_kq'})
        ec_df = ec_df[(ec_df['Date'] <= ed_date) & (ec_df['Date'] >= st_date)]
        ec_df = ec_df.reset_index(drop=True)
        ec_df = ec_df.rename(columns={'Close': 'Close_ec'})

        for i in corr_df['Code']:
            graph_df = df[df['Code'] == i]
            graph_df = pd.merge(graph_df, ks_df[['Date', 'Close_ks']], on='Date')
            graph_df = pd.merge(graph_df, kq_df[['Date', 'Close_kq']], on='Date')
            graph_df = pd.merge(graph_df, ec_df[['Date', 'Close_ec']], on='Date')
            graph_df = graph_df.drop('Unnamed: 0', axis=1)
            graph_df.set_index(keys=['Date'])

            # 히트맵 그래프
            heatmap_data = graph_df[['Num', 'Close', 'Volume', 'Close_ks', 'Close_kq', 'Close_ec']]
            colormap = plt.cm.PuBu
            plt.figure(figsize=(10, 8))
            plt.rc('font', family='NanumGothic')
            plt.title("상관관계 분석(8월 한달 간)", y=1.05, size=15)
            sns.heatmap(heatmap_data.astype(float).corr(), linewidths=0.1, vmax=1.0,
                        square=True, cmap=colormap, linecolor="white", annot=True, annot_kws={"size": 16})
            plt.show()

    def outlierGraph(self):
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
        plt.show()

        # 1. 왜도, 첨도
        sns.distplot(ne.values)
        print(ne.describe())
        plt.show()

        # boxplot 그리기
        sns.set(style="darkgrid")
        ax = sns.boxplot(y=ne.values)
        sns.swarmplot(y=ne.values, color="grey")
        plt.show()

        # 3. 테마 열 추가하기
        theme_df = self.theme_df.merge(self.outlierAnalysis(), how='inner', on='Code')
        theme_df = theme_df.iloc[:,1:5]

        # 4. pie chart 그리기
        theme = pd.DataFrame(columns=['Theme', 'Count'])
        for theme_str in theme_df['Theme']:
            # ', [, ] 특수문자 제거
            theme_str = theme_str.replace('\'', '').replace('[', '').replace(']', '').replace(' ', '')
            # ','를 기준으로 split해서 리스트로 만들
            theme_list = theme_str.split(',')

            # 1. theme에 해당 테마가 있는지 확인
            for i in theme_list:
                # if theme['Theme'].str.contains('i', case=False, regex=False):
                if theme['Theme'].isin([i]).any():
                    # 2. 있으면 해당 테마의 카운트 컬럼에 += 1을 해주기
                    theme.loc[theme['Theme'].isin([i]), 'Count'] += 1
                else:
                    # 3. 없으면 테마 컬럼에 해당 테마를 추가해주고, 카운트 컬럼에는 1을 넣기
                    theme = theme._append({'Theme': i, 'Count': 1}, ignore_index=True)

        theme_sorted = theme.sort_values(by='Count', ascending=False) # 'Count' values 정렬
        top_5 = theme_sorted.head(5) # Top5 출력
        dict_theme = top_5.to_dict(orient='list') # DataFrame 을 딕셔너리로 변환
        plt.rc('font', family='NanumGothic') # 그래프 한글 깨짐 방지

        # pie 차트 속성
        ratio = dict_theme['Count']
        labels = dict_theme['Theme']

        plt.pie(ratio,
                labels=labels,
                autopct='%.1f%%',
                startangle=0,
                counterclock=True,
                explode=[0.05, 0.05, 0.05, 0.05, 0.05],
                colors=sns.color_palette('viridis', len(labels)),
                wedgeprops={'width': 0.7, 'edgecolor': 'w', 'linewidth': 2},
                shadow=True)
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