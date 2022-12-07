from hashlib import new
import json 
import random

f = open("tokendata_final.json")
data = json.load(f)


# poolid: int
#     token0: str
#     token1: str 
#     reserve0: float
#     reserve1: float 
#     token0price: float
#     token1price: float
#     tvl: float

new_pools = []
for token1 in data:
    for token2 in data:
        if token1['TokenName'] < token2['TokenName']:
            f = token1['Price'] / token2['Price']
            reserve1 = random.randrange(5000000000000, 10000000000000)
            reserve2 = reserve1 * f
            new_pools.append({
                "token0": token1['TokenName'],
                "token1": token2['TokenName'],
                "reserve0": reserve1,
                "reserve1": reserve2,
                "token0price": token1['Price'],
                "token1price": token2['Price'],
                "tvl": reserve1 * token1['Price'] + reserve2 * token2['Price']
            })
            

h = open('pool_data.json', 'w')

json.dump(new_pools, h, indent=4)
h.close()
