import mysql.connector
import json 

mydb = mysql.connector.connect(
    host = "localhost",
    port=3306,
    user="root",
    password="hien1308",
    database="bakaswap"
)

f = open("tokendata_final.json")
data = json.load(f)

mycursor = mydb.cursor()

sql = "INSERT INTO Token (TokenName, TokenSymbol, TokenImage, Price, MarketCap) VALUES (%s, %s, %s, %s, %s)"

for token in data:
    val = (token['TokenName'], 
           token['TokenSymbol'], 
           token['TokenImage'], 
           token['Price'],
           token['MarketCap'])
    mycursor.execute(sql, val)
    
mydb.commit()

cp = open("pool_data.json")
pool_data = json.load(cp)

sql = "INSERT INTO Pool (token0, token1, reserve0, reserve1, tvl) VALUES (%s, %s, %s, %s, %s)"

for pool in pool_data:
    val = (pool['token0'], 
           pool['token1'],
           pool['reserve0'],
           pool['reserve1'],
           pool['tvl'])
    mycursor.execute(sql, val)
    
mydb.commit()