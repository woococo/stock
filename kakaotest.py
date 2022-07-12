import json
import requests

url = "https://kauth.kakao.com/oauth/token"

data = {
    "grant_type" : "authorization_code",
    "client_id" : "b57cdaa5057046acf918df0fefdb228c", # 가장 첫 화면에 있던 REST API 키 입력
    "redirect_uri" : "https://localhost.com",
    "code"         : "sKaJJPYpll9w1UiAqgdB3D_wY_0SxPBxPmfzaQ2qv97hjUUDO1hH-8YMLTVvzkpLLgiazwo9cusAAAGB8SQYBg" # 방금 받은 코드 키 입력

}
response = requests.post(url, data=data)
tokens = response.json()
print(tokens)