import traceback
import data_collection as dc

if __name__ == '__main__':
    try:
        # 인스턴스 생성
        new_data = dc.dataCollectionCls()

        # 모든 종목 코드 가져오기(KOSDAQ)
        codes = new_data.codeData()

        # 종목토론 데이터프레임 생성
        df = new_data.discussionData(codes)
    except:
        print("오류 발생")
        print(traceback.format_exc())