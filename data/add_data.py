from hashlib import new
import json 

f = open("tokendata.json")
data = json.load(f)


new_tokens = []
for token in data:
    new_tokens.append({
        "TokenName": token['name'],
        "TokenSymbol": token['symbol'],
        "TokenImage": token['image'],
        "Price": token['current_price']
    })

h = open('tokendata_final.json', 'w')

json.dump(new_tokens, h, indent=4)
h.close()
