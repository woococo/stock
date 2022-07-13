import json
import requests

# TOKEN Refresh
url = "https://kauth.kakao.com/oauth/token"

data = {
    "grant_type": "refresh_token",
    "client_id" : "b57cdaa5057046acf918df0fefdb228c",  
    "refresh_token" : 'pPBClccxPCCzJ36Imdt8oe_r_RKoif-AzaZ3sC7jCilvuQAAAYH2PqHU'  # 이번에는 갱신 토큰을 넣어 준다. 
}

response = requests.post(url, data=data)

tokens = response.json()
print(tokens)
access_token = tokens["access_token"]
print(access_token)