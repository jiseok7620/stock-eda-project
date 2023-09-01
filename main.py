import traceback
import data_collection as dc
import data_preprocessing as dp
import data_analysis as da

def exe_main(data_collect, data_preprocessing):
    # 인스턴스 생성
    new_data = dc.dataCollectionCls()
    pre_data = dp.dataPreprocessingCls()
    anl_data = da.dataAnalysisCls()

    # 1. 데이터 수집(data_clloect가 True인 데이터 만 수집됨)
    new_data.discussionNaverData(data_collect, new_data.codeData()[330:400], '2023-08-31', '2023-08-01') # 네이버 종목토론방 데이터 수집 # 285~299까지
    new_data.discussionDaumData(data_collect, new_data.codeData()[500:1000], '2023-08-31', '2023-08-01')  # 다음 종목토론방 데이터 수집
    new_data.stockData(data_collect, '2022-01-01') # 주식 데이터 수집 (2022-01-01~현재)
    new_data.indexData(data_collect, 'KS11') # 코스피 지수 데이터 수집
    new_data.indexData(data_collect, 'KQ11') # 코스닥 지수 데이터 수집
    new_data.indexData(data_collect, 'IXIC') # 나스닥 지수 데이터 수집
    new_data.indexData(data_collect, 'DJI') # 다우 지수 데이터 수집
    new_data.indexData(data_collect, 'US500') # S&P 지수 데이터 수집
    new_data.coinData(data_collect) # 비트코인 데이터 수집
    new_data.exchangeRateData(data_collect) # 환율 데이터 수집

    # 2. 데이터 전처리
    pre_data.stockPreprocessing(data_preprocessing, pre_data.naver_df, '2023-08-01', '2023-08-31') # 전처리 : - 일자, 게시글 수(sum), 종목코드, 종가, 거래량 - (1개월 간 종목들의 게시글 수 만들기)
    pre_data.discussionPreprocessing(data_preprocessing, pre_data.daum_df) # 전처리 : - 종목코드, 일자, 명사, 형용사, 동사 - (종목토론방 데이터 형태소 나누기)

    # 3. 데이터 분석
    anl_data.discussAnalysis() # 감성분석 1) 긍정, 부정, 중립 점수 매기기
    anl_data.commentsAnalysis() # 토론방 게시글 수와 주가의 관계 분석



if __name__ == '__main__':
    try:
        '''
            data_collect = 데이터를 수집 할 것 인지 [type : boolean]
        '''
        exe_main(False, False)
    except:
        print("오류 발생")
        print(traceback.format_exc())