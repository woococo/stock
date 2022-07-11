from __future__ import absolute_import, division, print_function, unicode_literals
import os, sys
import time
import json

# 사용자 정의 command를 위해서는 항상 포함되어야 한다. 
splunkhome = os.environ['SPLUNK_HOME']
sys.path.append(os.path.join(splunkhome, 'etc', 'apps', 'stock', 'lib')) # 추가되는 패키지들이 저장된 라이브러리 경로 
from splunklib.searchcommands import dispatch, GeneratingCommand, Configuration, Option, validators
from splunklib import six
from splunklib.six.moves import range

# 그 외에 필요한 패키지들... 
from urllib.request import urlopen
from bs4 import BeautifulSoup

# GeneratingCommand 를 상속받아서 새로운 명령어 생성
@Configuration()
class ReadStockCommand(GeneratingCommand):
    # 명령 파라미터 정의 "code" 를 파라미터로 받을 수 있게 정의함
    code = Option(require=True)

    # naver 에서는 다음페이지를 통해 현재 주식 가격 정보를 확인할 수 있다. 
    url = 'https://finance.naver.com/item/sise.nhn?code={}'

    #  구현해야 하는 함수
    def generate(self):
        # url에 파라미터로 받은 코드를 추가해서 전체 url 생성
        url = self.url.format(self.code)
        self.logger.info("Generating event with code %s" % (self.code))
        # url 호출
        with urlopen(url) as doc:
            content = doc.read()
            # 여기에서 약간의 삽질을... 리눅스에서는 "euc-kr"에 대한 encoding 이 되지 않아서 한글이 깨짐. 
            # 우선 한글이 꼭 필요한게 아니어서 ignore 하고 내용을 utf-8로 decode 하였는데,
            # 제대로 작동하기 위해서는 아래 코드를 사용하는 것이 좋음 (지금 환경에서 해결방법을 더 찾아봐야...)
            # soup = BeautifulSoup(doc, 'lxml', from_encoding="euc-kr")
            content = content.decode('utf-8', 'ignore') 
            soup = BeautifulSoup(content)
            # BeautifulSoup 을 이용하면 html을 파싱해서 원하는 정보를 가져올 수 있다. 
            cur_price = soup.find('strong', id='_nowVal').text.replace(",", "")
            cur_rate = soup.find('strong', id='_rate').text.strip()
            stock_name = self.code
        # 조회 된 내용을 바탕으로 메시지를 만들고 스플렁크 앱으로 전달해 준다.             
        raw = {"price": cur_price, "rate": cur_rate, "code":stock_name }
        yield {'_time': time.time(), '_raw': raw}


dispatch(ReadStockCommand, sys.argv, sys.stdin, sys.stdout, __name__)