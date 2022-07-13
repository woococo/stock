import json
import requests

url = "https://kauth.kakao.com/oauth/token"

data = {
    "grant_type" : "authorization_code",
    "client_id" : "b57cdaa5057046acf918df0fefdb228c", # 가장 첫 화면에 있던 REST API 키 입력
    "redirect_uri" : "https://localhost.com",
    "code"         : "Lz6SMSs3nEH4IAZukxGihPpfnvl6DfIqJTh2DSOoXpy_HPZat9mqKaBt6Qc5asFWArOoAgopb7gAAAGB9j1T9g" # 방금 받은 코드 키 입력

}
response = requests.post(url, data=data)
tokens = response.json()
print(tokens)

# https://kauth.kakao.com/oauth/authorize?client_id=b57cdaa5057046acf918df0fefdb228c&response_type=code&redirect_uri={REDIRECT_URI}