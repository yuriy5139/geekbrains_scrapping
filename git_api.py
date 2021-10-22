import requests

# task1

url = 'https://api.github.com/users/yuriy5139/repos'
headers = {"User-Agent": "curl/7.58.0", "Accept": "*/*"}
res = requests.get(url, headers=headers)
with open("repos.json", "w", encoding="utf8") as f:
    f.write(str(res.json()))
