import pandas as pd
from datetime import datetime
import requests
import json
import talib as tal


def log(message):
    print(datetime.now().strftime('%I:%M:%S')+" : "+message)


print("===================================================")
start_time = datetime.now()
log("START")
print("===================================================")

orders_array = []
open_orders = []
won = []
lost = []
aroonosc_min = -50
aroonosc_max = 50
adx = 50
capital = 240000
frequency = 10
qty_one = "off"
qty_max = 100000
volume_filter = 20000
price_filter_min = 100
price_filter_max = 25000

# https://tradeciety.com/10-most-profitable-candlestick-signals/
# https://www.ig.com/en/trading-strategies/16-candlestick-patterns-every-trader-should-know-180615

def scanning():
    log("PROCESSING INSTRUMENTS SYMBOLS")
    df_symbols = pd.read_csv('master/instruments.csv')

    for index, row in df_symbols.iterrows():

        response = pd.read_csv("data/"+row["tradingsymbol"]+".csv", usecols=[
                               'timestamp', 'open', 'high', 'low', 'close', 'volume', 'oi'])

        df = pd.DataFrame(response)

        if(df[df.columns[0]].count()):

            # tech analysis ends
            df["ADX"] = tal.ADX(
                high=df["high"], low=df["low"], close=df["close"])
            df["AROONOSC"] = tal.AROONOSC(high=df["high"], low=df["low"])
            df["ATR"] = tal.ATR(
                high=df["high"], low=df["low"], close=df["close"])
            df["CDLDOJI"] = tal.CDLDOJI(
                df["open"], df["high"], df["low"], df["close"])
            df["CDLENGULFING"] = tal.CDLENGULFING(
                df["open"], df["high"], df["low"], df["close"])
            df["CDLMORNINGSTAR"] = tal.CDLMORNINGSTAR(
                df["open"], df["high"], df["low"], df["close"])
            df["CDLHAMMER"] = tal.CDLHAMMER(
                df["open"], df["high"], df["low"], df["close"])
            df["CDLHARAMI"] = tal.CDLHARAMI(
                df["open"], df["high"], df["low"], df["close"])

            # tech analysis ends

            signal(row["tradingsymbol"], df)

    df_orders = pd.DataFrame(orders_array, columns=['timestamp', 'instrument',  'price', 'type',
                                                    'target', 'stoploss', 'qty', 'result', 'exit', 'trigger',
                                                    'brokerage', 'net'])

    sorted_df = df_orders.sort_values(by=['timestamp'], ascending=True)
    sorted_df.to_csv("backtest.csv")
    return


def signal(symbol, data):
    # log("SCANNING : "+symbol)
    order = {}
    orderType = ""
    for index, row in data.iterrows():

        if symbol in open_orders:
            if (order["type"] == "BUY" and order["qty"] > 0):
                temp = 0
                if(row["high"] > order["target"]):
                    if(temp == 0):
                        won.append(1)
                        order["trigger"] = row["high"]
                        order["result"] = 1
                        order["exit"] = row["timestamp"]
                        turnover = (order["price"]*order["qty"]) + \
                            (order["target"]*order["qty"])
                        order["brokerage"] = calculateBrokerage(turnover)
                        order["net"] = round(
                            ((order["target"] - order["price"]) * order["qty"])-order["brokerage"], 1)
                        orders_array.append(order)
                        open_orders.pop()
                        temp = 1
                if(row["low"] < order["stoploss"]):
                    if(temp == 0):
                        lost.append(0)
                        order["trigger"] = row["low"]
                        order["result"] = 0
                        order["exit"] = row["timestamp"]
                        turnover = (order["price"]*order["qty"]) + \
                            (order["stoploss"]*order["qty"])
                        order["brokerage"] = calculateBrokerage(turnover)
                        order["net"] = round(
                            ((order["stoploss"] - order["price"]) * order["qty"])-order["brokerage"], 1)
                        orders_array.append(order)
                        open_orders.pop()

            if (order["type"] == "SELL" and order["qty"] > 0):
                temp = 0
                if(row["low"] < order["target"]):
                    if(temp == 0):
                        won.append(1)
                        order["trigger"] = row["low"]
                        order["result"] = 1
                        order["exit"] = row["timestamp"]
                        turnover = (order["price"]*order["qty"]) + \
                            (order["target"]*order["qty"])
                        order["brokerage"] = calculateBrokerage(turnover)
                        order["net"] = round(
                            ((order["price"] - order["target"]) * order["qty"])-order["brokerage"], 1)
                        orders_array.append(order)
                        open_orders.pop()
                        temp = 1
                if(row["high"] > order["stoploss"]):
                    if(temp == 0):
                        lost.append(0)
                        order["trigger"] = row["high"]
                        order["result"] = 0
                        order["exit"] = row["timestamp"]
                        turnover = (order["price"]*order["qty"]) + \
                            (order["stoploss"]*order["qty"])
                        order["brokerage"] = calculateBrokerage(turnover)
                        order["net"] = round(
                            ((order["price"] - order["stoploss"]) * order["qty"])-order["brokerage"], 1)
                        orders_array.append(order)
                        open_orders.pop()

        if symbol not in open_orders:
            if ((row["ADX"] > adx) and (row["AROONOSC"] < aroonosc_min or row["AROONOSC"] > aroonosc_max)):
                # if ((row["AROONOSC"] < aroonosc_min or row["AROONOSC"] > aroonosc_max)):

                price = (row["open"] + row["high"] +
                         row["low"] + row["close"]) / 4

                orderType = ""
                candleType = ""

                # if ((row["AROONOSC"] > aroonosc_max)):
                #     orderType = "SELL"
                #     target = price - (row["ATR"]/4)
                #     stoploss = price + (row["ATR"]/4)

                # if ((row["AROONOSC"] < aroonosc_min)):
                #     orderType = "BUY"
                #     target = price + (row["ATR"]/4)
                #     stoploss = price - (row["ATR"]/4)
   
                if ((row["AROONOSC"] > aroonosc_max) and (row["close"] > row["open"])):  # uptrend 
                # if ((row["AROONOSC"] > aroonosc_max) and ((row["CDLDOJI"] > 100) or (row["CDLENGULFING"] > 100) or (row["CDLMORNINGSTAR"] > 100) or (row["CDLHAMMER"] > 100) or (row["CDLHARAMI"] > 100))):   # uptrend
                    orderType = "BUY"
                    target = row["high"]
                    stoploss = row["low"]
                    candle_upper = abs(row["high"]-row["close"])
                    candle_body = abs(row["close"]-row["open"])
                    candle_lower = abs(row["open"]-row["low"])
                    if((candle_body > candle_lower) and (candle_body > candle_upper) and (candle_lower > candle_upper)):
                        orderType = "BUY"
                        candleType = "green doji"
                    else:
                        orderType = ""

                if ((row["AROONOSC"] < aroonosc_min) and (row["close"] < row["open"])):  # downtrend 
                # if ((row["AROONOSC"] < aroonosc_min) and ((row["CDLDOJI"] < -100) or (row["CDLENGULFING"] < -100) or (row["CDLMORNINGSTAR"] < -100) or (row["CDLHAMMER"] < -100) or (row["CDLHARAMI"] < -100))):
                    orderType = "SELL"
                    target = row["low"]
                    stoploss = row["high"]
                    candle_upper = abs(row["high"]-row["open"])
                    candle_body = abs(row["open"]-row["close"])
                    candle_lower = abs(row["close"]-row["low"])
                    if((candle_body > candle_lower) and (candle_body > candle_upper) and (candle_upper > candle_upper)):
                        orderType = "SELL"
                        candleType = "red doji"
                    else:
                        orderType = ""

                # if ((row["AROONOSC"] > aroonosc_max) and (row["low"] == row["open"]) and (row["high"] == row["close"])):  # uptrend
                #     orderType = "BUY"
                #     target = row["close"]
                #     stoploss = row["open"]
                #     candleType = "green rectangle"

                # if ((row["AROONOSC"] < aroonosc_min) and (row["high"] == row["open"]) and (row["low"] == row["close"])):  # downtrend
                #     orderType = "SELL"
                #     target = row["close"]
                #     stoploss = row["open"]
                #     candleType = "red rectangle"

                # if ((row["AROONOSC"] > aroonosc_max) and (row["open"] == row["close"])):
                #     candleType = "nutral up doji"
                #     candle_upper = abs(row["high"]-row["close"])
                #     candle_lower = abs(row["open"]-row["low"])
                #     if(candle_upper < candle_lower):
                #         orderType = "BUY"
                #         target = row["high"]
                #         stoploss = row["low"]

                # if ((row["AROONOSC"] < aroonosc_min) and (row["open"] == row["close"])):
                #     candleType = "nutral down doji"
                #     candle_upper = abs(row["high"]-row["close"])
                #     candle_lower = abs(row["open"]-row["low"])
                #     if(candle_upper > candle_lower):
                #         orderType = "SELL"
                #         target = row["low"]
                #         stoploss = row["high"]

                if(orderType == "BUY" or orderType == "SELL"):
                    # RMS
                    rpt = round(((5*capital) / 100)/frequency, 0)
                    qty = round(rpt / 1, 0)
                    if((price-stoploss) != 0):
                        qty = round(rpt / (price - stoploss), 0)

                    if(qty_one == "on"):
                        qty = 1

                    if(qty > qty_max):
                        qty = qty_max

                    margin = capital * 2.5
                    total_price = qty * price
                    # print("QTY : "+str(qty))
                    if(total_price > margin):
                        qty = round((margin / price), 0)

                    order = {
                        'timestamp': row["timestamp"],
                        'type': orderType,
                        'instrument': symbol,
                        'product': 'MIS',
                        'target': round(target, 1),
                        'stoploss': round(stoploss, 1),
                        'qty': abs(qty),
                        'price': round(price, 1),
                        'volume': row["volume"],
                        'adx': row["ADX"],
                        'aroonosc': row["AROONOSC"],
                        'open': row['open'],
                        'high': row['high'],
                        'low': row['low'],
                        'close': row['close'],
                        'CDLDOJI': row['CDLDOJI']
                    }

                    if ((orderType != "") and (order["qty"] > 0) and (order["price"] < price_filter_max) and (order["price"] > price_filter_min) and (order["volume"] > volume_filter)):

                        order_time = (order["timestamp"]).replace('+0530', '')
                        timestamp = datetime.strptime(
                            order_time, '%Y-%m-%dT%H:%M:%S')
                        hours = timestamp.hour
                        timestamp = str(timestamp.hour) + ":" + \
                            str(timestamp.minute)

                        if(hours > 10 and hours < 15):
                            open_orders.append(symbol)
                            # print("candle : "+str(order["CDLDOJI"]))
                            log("ORDER FOUND > "+str(timestamp)+" : "+order["type"]+" @ "+str(
                                order["price"])+" / SL: "+str(order["stoploss"])+" / TAR : "+str(order["target"])+"/ QTY : "+str(order["qty"])+" / "+str(symbol)+"")

    return


def calculateBrokerage(turnover):
    # Brokerage = 0.03% or 20 which ever is lower
    # STT/CTT	= 0.025%
    # Transaction charges = 0.00345%
    # GST = 18% on (brokerage + transaction charges)
    # SEBI charges = ₹10 / crore
    # Stamp charges = 0.003% or ₹300 / crore on buy side
    brokerage = (0.03*turnover) / 100
    if(brokerage > 20):
        brokerage = 20
    # brokerage = 0
    stt_ctt = (0.025*turnover) / 100
    transaction_charges = (0.00345*turnover) / 100
    gst = (18*(transaction_charges+brokerage)) / 100
    sebi_charges = (10/10000000)*turnover
    stamp_charges = (0.025*(turnover/2)) / 100

    total = brokerage + stt_ctt + transaction_charges + \
        gst + sebi_charges + stamp_charges
    return round(total, 2)


scanning()

print("===================================================")
log("END")
print("===================================================")
end_time = datetime.now()
time_taken = divmod((end_time-start_time).total_seconds(), 60)[0]
print("Statistics     : "+str(won.count)+" : "+str(lost.count))
print("Start Time     : "+str(start_time))
print("End Time       : "+str(end_time))
print("Time Taken     : "+str(time_taken))
print("===================================================")
