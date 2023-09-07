import pandas as pd
import numpy as np
from mplfinance.original_flavor import candlestick2_ohlc
import matplotlib.gridspec as gridspec
import matplotlib.pyplot as plt
import json
import seaborn as sns
from collections import Counter
from wordcloud import WordCloud
import statistics
from scipy.stats import skew

class dataAnalysisCls:
    def data_list(self, wordname): # SentiWord_info의 json 사전의 긍정/부정/중립 값의 Score 가져오기
        with open('data/SentiWord_info.json', encoding='utf-8-sig', mode='r') as f:
            data = json.load(f)
        result = 9999
        result2 = 'None'
        for i in range(0, len(data)):
            if wordname in data[i]['word']:
                # 형태소 1
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
        df = pd.read_csv('datapreprocess/discussionnum.csv')

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
        df = pd.read_csv('datapreprocess/discussionnum.csv')
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
        df = pd.read_csv('datapreprocess/discussionnum.csv')
        df = df.astype({'Code' : 'str'})
        df['Code'] = df['Code'].apply(lambda x:x.zfill(6))
        corr_df = pd.concat([corr_df.head(2), corr_df.tail(2)])
        num = 0
        # 상관계수가 높은 상위 5개 종목을 그래프로 표현하기
        for i in corr_df['Code'] :
            num += 1
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
            #plt.show()

            # 이미지로 저장
            if num <= 2:
                plt.savefig('image/topcorr' + str(i) + '.png')
                plt.close()  # 창 닫기 및 메모리 해제
            else :
                plt.savefig('image/bottomcorr' + str(i) + '.png')
                plt.close()  # 창 닫기 및 메모리 해제

    def scatterGraph(self, outlier_df):
        df = pd.read_csv('datapreprocess/discussionnum.csv')
        df['Vol_Price'] = df['Close'] * df['Volume']

        # 평균 거래량, 평균 종가
        result_df = pd.DataFrame(columns=['Code','Trading Value','Changes Ratio','Comments'])
        for i in df['Code']:
            graph_df = df[df['Code'] == i]
            rate = [round(((a - b) / b) * 100, 2) for a, b in zip(graph_df.Close[1:len(graph_df) - 1], graph_df.Close[0:len(graph_df)])]
            #vol_mean = graph_df.Volume.mean() # 한달 평균 거래량
            vp_mean = graph_df.Vol_Price.mean() # 한달 평균 거래대금
            rate_mean = sum(rate) / len(rate) # 한달 평균 등락률
            Num_mean = graph_df.Num.mean()  # 한달 평균 게시글 수
            result_df.loc[len(result_df)] = [i, vp_mean, rate_mean, Num_mean]

        # 색깔 나타내기
        value = (result_df['Comments'] > df.Num.mean())
        df['color'] = np.where(value == True, "red", "#3498db")

        # plot
        sns.regplot(data=result_df, x="Trading Value", y="Changes Ratio", fit_reg=False, scatter_kws={'facecolors': df['color']})

        # plt.show() # 이미지 보기
        plt.savefig('image/scatter.png') # 이미지로 저장
        plt.close()  # 창 닫기 및 메모리 해제

    def heatmapGraph(self, corr_df):
        df = pd.read_csv('datapreprocess/discussionnum.csv')
        df = df.astype({'Code': 'str'})
        df['Code'] = df['Code'].apply(lambda x: x.zfill(6))

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

        corr_df = pd.concat([corr_df.head(3), corr_df.tail(3)])
        num = 0
        # 상관계수가 높은 상위, 하위 2개 종목을 그래프로 표현하기
        for i in corr_df['Code']:
            num += 1
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
            plt.title("상관관계 분석", y=1.05, size=15)
            sns.heatmap(heatmap_data.astype(float).corr(), linewidths=0.1, vmax=1.0,
                        square=True, cmap=colormap, linecolor="white", annot=True, annot_kws={"size": 16})

            #plt.show() # 이미지 보여주기
            # 이미지로 저장
            if num <= 3:
                plt.savefig('image/topheatmap' + str(i) + '.png')
                plt.close()  # 창 닫기 및 메모리 해제
            else:
                plt.savefig('image/bottomheatmap' + str(i) + '.png')
                plt.close()  # 창 닫기 및 메모리 해제

    def outlierGraph(self):
        df = pd.read_csv('datapreprocess/discussionnum.csv')

        # 종목 코드 별로 그룹화하여 게시글 수의 합 구하기
        gr = df.groupby('Code').sum()
        ne = gr['Num']
        # print(ne.idxmax()) # max : 047310(파워로직스)

        # 범주화하기
        list = [0, ne.max()/512, ne.max()/256, ne.max()/128, ne.max()/64, ne.max()/32, ne.max()/16, ne.max()/8, ne.max()/4, ne.max()/2, ne.max()]
        labels = [str(round(int(ne.max()/512),-1)), str(round(int(ne.max()/256),-1)), str(round(int(ne.max()/128),-2)),
                  str(round(int(ne.max()/64),-2)), str(round(int(ne.max()/32),-2)), str(round(int(ne.max()/16),-2)),
                  str(round(int(ne.max()/8),-2)), str(round(int(ne.max()/4),-2)), str(round(int(ne.max()/2),-3)),
                  str(round(int(ne.max()),-3))]
        new_sr = pd.cut(ne, list, labels=labels)

        # 범주별로 종목의 개수 count하기
        new_sr = new_sr.value_counts()
        new_sr = new_sr.sort_index()

        # barplot 생성 (Matplotlib의 bar)
        plt.rc('font', family='NanumGothic') # 그래프 한글 깨짐 방지
        plt.plot(new_sr.index, new_sr.values, 'ro', linestyle='-')
        plt.bar(new_sr.index, new_sr.values, color='skyblue', edgecolor='gray')

        # 숫자 표시하기
        for i in range(10):
            plt.text(i, new_sr[i], str(new_sr[i]), ha='center', va='bottom')

        # 축 및 제목 설정
        plt.xlabel('게시글 수')
        plt.ylabel('종목 수')
        plt.title('범주화 그래프')
        #plt.show() # 이미지 보여주기
        plt.savefig('image/category.png') # 이미지로 저장
        plt.close()  # 창 닫기 및 메모리 해제

        #1. 왜도, 첨도
        # print(ne)
        # print(ne.info())
        # print('중앙값 :', statistics.median(ne))
        # print('최빈값 :', statistics.mode(ne))
        # print('평균값 :', round(sum(ne) / len(ne),2))
        # print('평균값 :', skew(ne))
        sns.distplot(ne.values,
                     color='skyblue',
                     kde_kws={'color': 'red', 'linewidth': 1})
        # 그래프 제목 설정
        plt.title('Distribution Plot')
        # 축 레이블 설정
        plt.xlabel('Number of posts')
        plt.ylabel('Density')
        # plt.show() # 이미지 보여주기
        plt.savefig('image/skewness.png')  # 이미지로 저장
        plt.close()  # 창 닫기 및 메모리 해제

        # boxplot 그리기
        sns.set(style="white")
        ax = sns.boxplot(y=ne.values,
                        color = 'skyblue',
                        linewidth = 1)
        sns.swarmplot(y=ne.values,
                      color="red",
                      size=1)
        # y축 범위 설정
        plt.ylim(0, 6000)
        # y축 레이블 설정
        plt.ylabel('Number of posts')
        #plt.show() # 이미지 보여주기
        plt.savefig('image/boxplot.png') # 이미지로 저장
        plt.close() # 창 닫기 및 메모리 해제

        # 3. 테마 열 추가하기
        theme_df = pd.read_csv('datapreprocess/stocktheme.csv')
        theme_df = theme_df.merge(self.outlierAnalysis(), how='inner', on='Code')
        theme_df = theme_df.iloc[:, 1:5]

        # 4. pie chart 그리기
        theme = pd.DataFrame(columns=['Theme', 'Count'])
        theme_dup_df = pd.DataFrame(columns=['Name', 'Num', 'Theme'])
        for name, num, theme_str in zip(theme_df['Name'], theme_df['Num'], theme_df['Theme']):

            if str(theme_str) == 'nan':
                continue
            # ', [, ] 특수문자 제거
            theme_str = theme_str.replace('\'', '').replace('[', '').replace(']', '').replace(' ', '')
            # ','를 기준으로 split해서 리스트로 만들
            theme_list = theme_str.split(',')

            # 1. theme에 해당 테마가 있는지 확인
            for i in theme_list:
                # theme_dup_df에 종목과 테마 넣기
                theme_dup_df = theme_dup_df._append({'Name': name, 'Num' : num, 'Theme': i}, ignore_index=True)
                if theme['Theme'].isin([i]).any():
                    # 2. 있으면 해당 테마의 카운트 컬럼에 += 1을 해주기
                    theme.loc[theme['Theme'].isin([i]), 'Count'] += 1
                else:
                    # 3. 없으면 테마 컬럼에 해당 테마를 추가해주고, 카운트 컬럼에는 1을 넣기
                    theme = theme._append({'Theme': i, 'Count': 1}, ignore_index=True)

        theme_sorted = theme.sort_values(by='Count', ascending=False) # 'Count' values 정렬
        top_5 = theme_sorted.head(5) # Top5 출력
        pie_df = pd.merge(top_5, theme_dup_df, on='Theme')
        pie_df['Rank'] = pie_df['Num'].rank(method='min', ascending=False)

        def assign_value(rank): # 조건에 따라 값을 할당하는 함수 정의
            if rank <= 10:
                return 50
            elif rank <= 20:
                return 45
            elif rank <= 30:
                return 41
            elif rank <= 40:
                return 38
            elif rank <= 50:
                return 36
            elif rank <= 60:
                return 35
            else:
                return None
        pie_df['Newnum'] = pie_df['Rank'].apply(assign_value)

        def get_label_rotation(angle, offset): # 레이블의 회전과 정렬 도우미 함수
            rotation = np.rad2deg(angle + offset)
            if angle <= np.pi:
                alignment = "right"
                rotation = rotation + 180
            else:
                alignment = "left"
            return rotation, alignment

        def add_labels(angles, values, labels, offset, ax): # 플롯에 레이블을 추가하는 함수
            padding = 4
            # Iterate over angles, values, and labels, to add all of them.
            for angle, value, label, in zip(angles, values, labels):
                angle = angle

                # Obtain text rotation and alignment
                rotation, alignment = get_label_rotation(angle, offset)
                # And finally add the text
                ax.text(
                    x=angle,
                    y=value + padding,
                    s=label,
                    ha=alignment,
                    va="center",
                    rotation=rotation,
                    rotation_mode="anchor")

        # 그룹화하기
        GROUP = pie_df['Theme'].values

        # 표시할 값
        VALUES = pie_df["Newnum"].values
        LABELS = pie_df["Name"].values

        # 회전
        PAD = 3
        ANGLES_N = len(VALUES) + PAD * len(np.unique(GROUP))
        ANGLES = np.linspace(0, 2 * np.pi, num=ANGLES_N, endpoint=False)
        WIDTH = (2 * np.pi) / len(ANGLES)
        
        # 그룹 사이즈(그룹별 몇개 표시할 것인지)
        GROUPS_SIZE = [len(i[1]) for i in pie_df.groupby("Theme")]
        GROUPS_SIZE = sorted(GROUPS_SIZE, reverse=True)

        # idx 리스트, offset
        offset = 0
        OFFSET = np.pi / 2
        IDXS = []
        for size in GROUPS_SIZE:
            IDXS += list(range(offset + PAD, offset + size + PAD))
            offset += size + PAD

        # Initialize Figure and Axis
        fig, ax = plt.subplots(figsize=(20, 10), subplot_kw={"projection": "polar"})
        plt.rc('font', family='NanumGothic')  # 그래프 한글 깨짐 방지

        ax.set_theta_offset(OFFSET)
        ax.set_ylim(-50, 50)
        ax.set_frame_on(False)
        ax.xaxis.grid(False)
        ax.yaxis.grid(False)
        ax.set_xticks([])
        ax.set_yticks([])
        
        # 색상 지정
        COLORS = [f"C{i}" for i, size in enumerate(GROUPS_SIZE) for _ in range(size)]

        # Add bars
        ax.bar(
            ANGLES[IDXS], VALUES, width=WIDTH, linewidth=2,
            color=COLORS, edgecolor="white")

        # Add labels
        add_labels(ANGLES[IDXS], VALUES, LABELS, OFFSET, ax)
        gr_df = pie_df.drop_duplicates(subset='Theme')
        name_list = []
        for index, row in gr_df.iterrows():
            name = row[0] + '\n(' + str(row[1]) + ')'
            name_list.append(name)

        offset = 0
        for group, size in zip(name_list, GROUPS_SIZE):
            # Add line below bars
            x1 = np.linspace(ANGLES[offset + PAD], ANGLES[offset + size + PAD - 1], num=50)
            ax.plot(x1, [-5] * 50, color="#333333")

            # Add text to indicate group
            ax.text(
                np.mean(x1), -20, group, color="#333333", fontsize=12,
                fontweight="bold", ha="center", va="center")

            # Add reference lines at 20, 40, 60, and 80
            x2 = np.linspace(ANGLES[offset], ANGLES[offset + PAD - 1], num=50)
            ax.plot(x2, [20] * 50, color="#bebebe", lw=0.8)
            ax.plot(x2, [40] * 50, color="#bebebe", lw=0.8)
            ax.plot(x2, [60] * 50, color="#bebebe", lw=0.8)
            ax.plot(x2, [80] * 50, color="#bebebe", lw=0.8)

            offset += size + PAD

        #plt.show()
        plt.savefig('image/piechart.png') # 이미지로 저장
        plt.close() # 창 닫기 및 메모리 해제

    def wordCloudGraph(self): # 워드클라우드 그래프 만들기 (빈도기반분석)
        df = pd.read_csv('datapreprocess/morpheme.csv')
        df = df.astype({'Code': 'str'})
        df['Code'] = df['Code'].apply(lambda x: x.zfill(6))

        codes = ['250000', '053030']
        for i in codes:
            test_df = df[df['Code'] == i]

            nouns = []
            adjectives = []
            verbs = []
            for word1, word2, word3 in zip(test_df['Noun'], test_df['Adjective'], test_df['Verb']):
                # ', [, ] 특수문자 제거
                word_nouns_list = word1.replace('\'', '').replace('[', '').replace(']', '').replace(' ', '')
                word_adjectives_list = word2.replace('\'', '').replace('[', '').replace(']', '').replace(' ', '')
                word_verbs_list = word3.replace('\'', '').replace('[', '').replace(']', '').replace(' ', '')

                # ','를 기준으로 split해서 리스트로 만들
                word_nouns_list = word_nouns_list.split(',')
                word_adjectives_list =word_adjectives_list.split(',')
                word_verbs_list = word_verbs_list.split(',')

                for aa,bb,cc in zip(word_nouns_list, word_adjectives_list, word_verbs_list):
                    nouns.append(aa)
                    adjectives.append(bb)
                    verbs.append(cc)

            # 명사, 형용사, 동사 전처리
            noucs_filtered_list = [word for word in nouns if len(word) > 1] # 명사는 1글자 이상만 추출
            adjectives_filtered_list = [word for word in adjectives if len(word) > 1]
            verbs_filtered_list = [word for word in verbs if len(word) > 1]

            # 합친 리스트
            all_list = noucs_filtered_list + verbs_filtered_list

            # 가장 많이 나온 단어부터 n개를 지정
            counts = Counter(all_list)
            tags = counts.most_common(50)

            # wordcloud 생성
            wc = WordCloud(font_path='data/malgunbd.ttf', background_color="black", max_font_size=60)
            cloud = wc.generate_from_frequencies(dict(tags))

            # wordcloud 띄우기
            plt.figure(figsize=(16, 8))
            plt.axis('off')
            plt.imshow(cloud)
            #plt.show() # 이미지 보여주기
            plt.savefig('image/wordcloud'+str(i)+'.png') # 이미지로 저장
            plt.close()  # 창 닫기 및 메모리 해제

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