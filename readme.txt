m nov 29 : 1-0
t nov 30 : 1-0
w dec 01 : 1-0
t dec 02 : 5-2
f dec 03 : 3-3

observation :
- introduce hammer pair ( T up/down )
- possibly remove (rectangle and nutral) candles pair and continue for week
- keep all 3 pair of candle and do it with 2 minutes time frame (take care of qty set up)
- keep 1(doji) pair of candle and do it with 2 minutes time frame (take care of qty set up)

==========================
research status (to try)
- scalping to 1 minute or 2 minute (suggested to TAR SL are in H - O/C and O - /CL)
- ta lib candlestick patterns
- sma cross over

- manual trading (go in trend) trail SL to prev candle wrt its trend
- trailing stoploss (https://kite.zerodha.com/oms/orders/regular/211126402747848)
Request Method: PUT
variety: regular
exchange: NSE
tradingsymbol: PAYTM
transaction_type: SELL
order_type: SL-M
quantity: 1
price: 0
product: MIS
validity: DAY
disclosed_quantity: 0
trigger_price: 1600
squareoff: 0
stoploss: 0
trailing_stoploss: 0
user_id: VM7727
order_id: 211126402747848
parent_order_id: 








============================
- clean logs
- dates config
- refresh token
- check test mod on
- open crons
============================

#*/1 15 * * 1-5  cd ~/Web/AlgoTrade/scanner/ && python3 windup.py  > logs/windup/`date +\%H:\%M`.log 2>&1
#*/1 10,11,12,13,14 * * 1-5  cd ~/Web/AlgoTrade/scanner/ && python3 cleaner.py  > logs/cleaner/`date +\%H:\%M`.log 2>&1
#*/2 10,11,12,13,14 * * 1-5  cd ~/Web/AlgoTrade/scanner/ && python3 scanner.py  > logs/scanner/`date +\%H:\%M`.log 2>&1
