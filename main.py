import traceback

import pandas as pd

import data_collection as dc

def exe_main(data_collect):
    # 인스턴스 생성
    new_data = dc.dataCollectionCls()

    # 1. 데이터 수집(data_clloect가 True인 데이터 만 수집됨)
    #new_data.discussionData(data_collect, new_data.codeData(), '2023-07-31') # 종목토론방 데이터 수집
    new_data.discussionNaverData(True, new_data.codeData()[1000:1002], '2023-07-31') # 네이버 종목토론방 데이터 수집
    new_data.discussionDaumData(data_collect, new_data.codeData()[500:1000], '2023-07-31')  # 다음 종목토론방 데이터 수집
    new_data.stockData(data_collect, '2022-01-01') # 주식 데이터 수집 (2022-01-01~현재)
    new_data.indexData(data_collect, 'KS11') # 코스피 지수 데이터 수집
    new_data.indexData(data_collect, 'KQ11') # 코스닥 지수 데이터 수집
    new_data.indexData(data_collect, 'IXIC') # 나스닥 지수 데이터 수집
    new_data.indexData(data_collect, 'DJI') # 다우 지수 데이터 수집
    new_data.indexData(data_collect, 'US500') # S&P 지수 데이터 수집
    new_data.coinData(data_collect) # 비트코인 데이터 수집
    new_data.exchangeRateData(data_collect) # 환율 데이터 수집

    # 2. 데이터 전처리


if __name__ == '__main__':
    try:
        '''
            data_collect = 데이터를 수집 할 것 인지 [type : boolean]
        '''
        exe_main(False)
    except:
        print("오류 발생")
        print(traceback.format_exc())