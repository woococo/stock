import json
import requests

url = "https://kapi.kakao.com/v2/api/talk/memo/default/send"

access_token="NLS270EZeKFh6Pl2-NnmC387KyIZdwsD-iwV7OyvCilvuQAAAYH2PqHW" # 위에서 받은 접근 토큰
# 사용자 토큰
headers = {
    "Authorization": "Bearer " + access_token
}

# 전송할 데이터 포맷
data = {
    "template_object" : json.dumps({ "object_type" : "text",
                                     "text" : "Hello, world!",
                                     "link" : {
                                                 "web_url" : "www.splunk.com"
                                              }
    })
}

response = requests.post(url, headers=headers, data=data)
print(response.status_code)
if response.json().get('result_code') == 0:
    print('메시지를 성공적으로 보냈습니다.')
else:
    print('메시지를 성공적으로 보내지 못했습니다. 오류메시지 : ' + str(response.json()))