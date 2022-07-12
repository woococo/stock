# Splunk 에서 데이터를 불러오기위한 라이브러리 import
import splunklib.results as results
import splunklib.client as client

import io, os, sys, types, datetime, time
import pandas as pd

"""
스플렁크에 SPL 을 수행해서 데이터를 가져온다. 
@host : 스플렁크 설치 호스트
@port:  스플렁크 REST API 접속 포트 (8089)
@username: 스플렁크 접속 계정
@password: 스플렁크 접속 패스워드
"""
class SplunkDataReader():
    def __init__(self, host, port, username, password):
        self._host = host
        self._port = port
        self._username = username
        self._password = password
        self._service = None

    """
    스플렁크에 접속한다.
    """
    def connect(self):
        self._service = client.connect(host=self._host,
                port = self._port,
                username = self._username,
                password = self._password);

    """
    스플렁크에 SPL 을 수행해서 데이터를 읽어서 결과를 리턴한다. 
    @searchquery_normal:  일반적인 SPL  문
    """
    def execute_query(self, searchquery_normal,
                  kwargs_normalsearch={"exec_mode":"normal"},
                  kwargs_options={"output_mode":"csv", "count":100000}):
        # 스플렁크에 SPL 을 수행하면 해당 job 이 생성된다. 이 Job을 통해 async  하게 데이터를 가져와야 한다. 
        job = self._service.jobs.create(searchquery_normal, **kwargs_normalsearch)

        #  모든 작업이 끝날 때까지 대기하기 위해 Loop 수행 (@TODO 여러 쿼리를 수행해야 하는 경우 Thread 처리해야 함)
        while True:
            # 작업이 실행 준비 되었는지 체크하고  아니면 계속 모니터링
            while not job.is_ready():
                pass
            # 현재 작업이 수행 중에 있고, 작업의 상태를 모니터링 한다. 
            stats = {"isDone":job["isDone"], "doneProgress":float(job["doneProgress"]) *100,
                "scanCount":int(job["scanCount"]), "eventCount":int(job["eventCount"]),
                "resultCount":int(job["resultCount"])}

            status = ("\r%(doneProgress)03.1f%% %(scanCount)d scanned"
                 "%(eventCount)d matched %(resultCount)d results") % stats
            # 작업 상태를 사용자를 위해 출력
            sys.stdout.write(status)
            sys.stdout.flush()

            # 작업 상태가 완료가 되었다면 루프를 빠져나감
            if stats["isDone"] == "1":
                sys.stdout.write("\nDone!")
                break;
            time.sleep(0.5)

        # 작업 결과를 받아오고, 데이터프레임에 저장
        csv_results = job.results(**kwargs_options).read()
        df = pd.read_csv(io.BytesIO(csv_results), encoding='utf8', sep=',')
        # 작업을 제거
        job.cancel()
        # 결과 리턴
        return df