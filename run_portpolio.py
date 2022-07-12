# 방금 만들 파이썬 파일들 import
from splunk_data_reader import SplunkDataReader
from monte_sim import MonteCarloSim

import pandas as pd
import numpy as np
import argparse
from datetime import datetime, timedelta
import json
import os
import sys
from random import seed
from random import randinte
import time
import requests
import urllib3

# kospi_200. csv 파일을 읽기 위한 경로 설정
CONF_PATH=os.path.dirname(os.path.abspath(__file__))
LOG_PATH=CONF_PATH + '/stock'
# kospi_200.csv 에서 주식 종목 리스트를 읽어온다. 
def getCodeList():
    df = pd.read_csv(CONF_PATH + "/kospi_200.csv", dtype=str)
    return df.code.values

seed(datetime.now()) # 랜덤 시드 초기화
"""
kospi 200 목록에서 종목을 선택한다. 
 @codebook[] :  전체 종목 리스트
 @codes[]:  필수적으로 포함시키고 싶은 종목 목록
 @ num: 총 선택할 종목 수
"""
def genRandomCode(codebook, codes, num):
    random_ranges = len(codebook)
    # num=5   이고 필수적으로 포함시켜향 종목의 수가 2 이면 3개의 종목이 랜덤하게 선택된다. 
    itera = num - len(codes)
    ran_code = [ code for code in codes]

    for _ in range(itera):
        while True:
            # 랜덤하게 종목 코드 하나 선택
            code = codebook[randint(0, random_ranges-1)] + ".KS"
            # 이미 포함 된 코드이면  pass
            if code in ran_code: 
                pass
            # 새로운 코드면 추가
            else:
                ran_code.append(code) 
                break

    return ran_code

"""
스플렁크에서 필요한 데이터를 읽어온다. 
 @reader:  스플렁크 접속 객체
 @codes[]:   주식 종목 리스트
 @days:  가져올 데이터의 날 수 
"""
def readData(reader, codes, days=180):
    #스플렁크 SPL 문
    splunk_query="""
        search index=kospi {codes} earliest={days}
        | rename Date as date
        | chart latest(Close) as value by date, code
    """
    code_str = " OR ".join(codes)
    days_str = "-" + str(days) + "d@"

    # SPL을 수행해서 데이터를 가져온다. 
    df = reader.execute_query(splunk_query.format(codes=code_str, days=days_str))
    return df

"""
HEC 를 통해 스플렁크에 결과 데이터를 저장한다. 
 @host: 스플렁크 접속 서버
 @token: 스플렁크에서 발급한 접속 토근
"""
authToken = "XXXXXXX-XXXX-XXXX-XXXX-XXXXXXXXXXXX"  # @TODO 나의 토큰으로 대체
splunkhost = "localhost" # @TODO 나의 서버 주소로 대체
def splunkHec(host, token, data):
    url="https://" + host + ":8088/services/collector/event"
    authHeader = {'Authorization': 'Splunk ' + token}
    payload = {}
    payload.update({"index":"monte"})   # "monte"  라는 인덱스에 저장
    payload.update({"sourcetype":"_json"})  # "_json" 소스타입으로 저장
    payload.update({"source":"monte_sim.py"}) # "monte_sim.py" 소스로 저장
    payload.update({"event": data}) # "저장할 데이터 메시지"
    r = requests.post(url, headers=authHeader, json=payload, verify=False)  # 스플렁크로 데이터 전송

"""
반복해서 임의의 코드 종목을 선택하여 최상의 종목 조합을 찾음
 @ reader: 스플렁크 접속 객체
 @ codebook: 주식 종목 리스트
 @  required_codes: 반드시 포트폴리오에 포함해야할 코드 목록
 @ num: 포트폴리오를 구성할 주식 종목의 수
 @ repeat: 반복 횟수 
"""
def findBestPortpolio(reader, codebook, required_codes, num, repeat=10000):
    # 몬테카를로 시뮬레이터 객체 생성
    sim = MonteCarloSim()
    # repeat  만큼 반복해서 주식 종목 선택 수행
    for idx in range(repeat): 
        # 랜덤한 주식 종목을 가져온다. 
        c = genRandomCode(codebook, required_codes, num)
        # 선택된 주식 종목에 대해서 스플렁크에서 해당 데이터를 가져온다. 
        df = readData(reader, c, days)
        # 몬테카를로 시뮬레이터를 수행한다. 
        monte_df = sim.fit(df)
       # Sharpe 값이 가장 좋은 항목을 선택한다. 
        monte_max = monte_df.loc[monte_df['Sharpe'].idxmax()]

        # 선택된 데이터에 대해서 스플렁크에 전달할 데이터 모양을 만든다. 
        dic = {}
        codes = []
        rates = []
        for key in monte_max.keys(): 
            if key not in ['Sharpe', 'Returns', 'Risk']:
                codes.append(key)
                rates.append(monte_max[key])
            else:
                dic[key] = monte_max[key]   
           
        dic['idx'] = idx
        dic["code"] = codes
        dic["rate"] = rates
        dic["date"] = datetime.now().strftime("%Y-%m-%d")

        data = json.dumps(dic)  
        # 스플렁크로 해당 데이터를 보낸다. 
        splunkHec(splunkhost, authToken, data)

# 인자로 전달되는 코드의 유효성 체크
def verifyCode(required):
    codes = required.split(",")
    codes = [ v + ".KS" if len(v)==6  else v for v in codes]
    return codes;

if __name__ == "__main__":
    # 전달받는 파라미터 설정
    parser = argparse.ArgumentParser()
    parser.add_argument('--days', help='days help')
    parser.add_argument('--num', help='num help')
    parser.add_argument('--required', help='required help')
    parser.add_argument('--repeat', help='repeat help')

    args = parser.parse_args()
    
    if args.days:
        days = int(args.days)
    else:
        days = 180

    if args.num:
        num = int(args.num)
    else:
        num = 5

    if args.repeat:
        repeat = int(args.repeat)
    else:
        repeat = 1000

    codes =[]
    if args.required:
        codes = verifyCode(args.required);

    # 주식 종목 리스트 읽기
    codebook = getCodeList()
    # 스플렁크 접속 객체 생성 @TODO 나의 접속 정보로 수정
    reader = SplunkDataReader("localhost", 8089, "my_account", "my_password")
    # 스플렁크에 접속
    reader.connect()
    #  포트 폴리오 검색 수행
    findBestPortpolio(reader, codebook, codes, num, repeat)