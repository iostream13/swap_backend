import requests
import json

url = "https://api.coingecko.com/api/v3/coins/markets?vs_currency=usd&order=market_cap_desc&per_page=100&page=1&sparkline=false"

payload={}
headers = {
  'accept': 'application/json'
}

response = requests.request("GET", url, headers=headers, data=payload)

f = open("tokendata.json", 'w')

data = json.loads(response.text)

json.dump(data, f, indent=4)

f.close()

