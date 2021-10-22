import json, requests

# task2

url = 'https://api.foursquare.com/v2/venues/explore'

headers = {"User-Agent": "curl/7.58.0", "Accept": "*/*"}

params = dict(
    client_id='MF0252C1ATAHNTEZ3PBDBY0XZSWKBPD2ZYSNFEK4RPMYYQEY',
    client_secret='MHYBF2FVWQPOMRLN3VVLHCFTBCNJIRWFWAHA5UEMM5TSDV2L',
    v='20211021',
    ll='40.7243,-74.0018',
    query='coffee',
    limit=1
)
resp = requests.get(url=url, params=params, headers=headers)
data = json.loads(resp.text)
with open("foursquare.json", "w", encoding="utf8") as f:
    f.write(str(data))
