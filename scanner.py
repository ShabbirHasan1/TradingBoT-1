# SCALPER
from datetime import datetime
import requests
import pandas as pd
import json
import talib as tal
import json


def log(message):
    print(datetime.now().strftime('%I:%M:%S')+" : "+message)


print("===================================================")
start_time = datetime.now()
log("START")
print("===================================================")

with open("token.json") as json_file:
    json_data = json.load(json_file)
    kite_token = json_data["kite_token"]

# from_date = datetime.
# now().strftime('%Y-%m-%d')
from_date = "2022-08-12"
to_date = datetime.now().strftime('%Y-%m-%d')

# actual
# aroonosc_min = -50
# aroonosc_max = 50
# adx = 50

# test
aroonosc_min = -50
aroonosc_max = 50
adx = 50

min_candle_time = 60
max_candle_time = 240
capital = 10000
frequency = 20
volume_filter = 20000
price_filter_min = 50
price_filter_max = 50000
upper_circuit = 8
lower_circuit = -8
upper_circuit_alert = 10
lower_circuit_alert = -10
qty_max = 100000
test_mod = "off"
emergency_exit = "off"
qty_one = "off"
# -----------------------------------------------------------------


def scanning():
    if((emergency_exit == "on")):
        print("Emergency Exit ON")
        return

    total_data_points = 0
    log("PROCESSING INSTRUMENTS SYMBOLS")
    print("-----------------------------------------------")
    df_symbols = pd.read_csv('master/instruments_all.csv')
    for index, row in df_symbols.iterrows():
        endpoint = "https://kite.zerodha.com/oms/instruments/historical/"
        code = str(row["instrument_token"])
        interval = "/5minute"
        headers = {'content-type': 'application/json',
                   "authorization": kite_token}
        url = endpoint + code + interval
        params = (
            ('user_id', 'XMK294'),
            ('oi', '1'),
            ('from', str(from_date)),
            ('to', str(to_date)),
        )
        response = requests.get(
            url, timeout=600, headers=headers, params=params).json()

        if(response['data']['candles'] and response["status"] == "success"):

            df = pd.DataFrame(response['data']['candles'], columns=[
                'timestamp', 'open', 'high', 'low', 'close', 'volume', 'oi'])

            if(df[df.columns[0]].count()):

                # tech analysis starts
                df["ADX"] = tal.ADX(
                    high=df["high"], low=df["low"], close=df["close"])
                df["AROONOSC"] = tal.AROONOSC(
                    high=df["high"], low=df["low"], timeperiod=14)
                df["ATR"] = tal.ATR(high=df["high"], low=df["low"], close=df["close"])
                df["RSI"] = tal.RSI(df['close'])
                # df["CDLDOJI"] = tal.CDLDOJI(df["open"],df["high"],df["low"],df["close"])
                # tech analysis ends

                signal(row["tradingsymbol"], df)

        else:
            print("No data available")
    return


def signal(symbol, data):
    log("SCANNING : "+symbol)
    order = {}
    orderType = ""
    tempDayOpenCheck = 0
    tempDayOpenTimestamp = str(to_date)+"T09:15:00+0530"
    dayOpen = 0
    circuit = 0
    circuit_validation = "valid"
    rpt = 0
    aroonosc_now = 0
    adx_now = 0
    for index, row in data.iterrows():
        adx_now = round(row["ADX"], 2)
        aroonosc_now = round(row["AROONOSC"], 2)
        if(row["timestamp"] == str(tempDayOpenTimestamp) and tempDayOpenCheck == 0):
            dayOpen = row["open"]
            tempDayOpenCheck = 1
        if(dayOpen != 0):
            circuit = round(((row["close"] - dayOpen)/dayOpen)*100, 2)

        if(dayOpen != 0 and (circuit < upper_circuit and circuit > lower_circuit)):
            circuit_validation = "valid"
        else:
            circuit_validation = "invalid"

        if ((row["ADX"] > adx) and (row["AROONOSC"] < aroonosc_min or row["AROONOSC"] > aroonosc_max)):
            price = (row["open"] + row["high"] + row["low"] + row["close"])/4
            orderType = ""
            candleType = ""
            # green doji
            if ((row["AROONOSC"] > aroonosc_max) and (row["close"] > row["open"])):  # uptrend
                orderType = "BUY"
                target = row["high"]
                stoploss = row["low"]
                candle_upper = abs(row["high"]-row["close"])
                candle_body = abs(row["close"]-row["open"])
                candle_lower = abs(row["open"]-row["low"])
                if((candle_body > candle_lower) and (candle_body > candle_upper) and (candle_lower > candle_upper)): 
                    orderType = "BUY"
                    candleType = "green"
                else:
                    orderType = ""

            # red doji
            if ((row["AROONOSC"] < aroonosc_min) and (row["close"] < row["open"])):  # downtrend
                orderType = "SELL"
                target = row["low"]
                stoploss = row["high"]
                candle_upper = abs(row["high"]-row["open"])
                candle_body = abs(row["open"]-row["close"])
                candle_lower = abs(row["close"]-row["low"])
                if((candle_body > candle_lower) and (candle_body > candle_upper) and (candle_upper > candle_upper)):
                    orderType = "SELL"
                    candleType = "red"
                else:
                    orderType = ""

            # green rectangle
            # if ((row["AROONOSC"] > aroonosc_max) and (row["low"] == row["open"]) and (row["high"] == row["close"])):  # uptrend
            #     orderType = "BUY"
            #     target = row["close"]
            #     stoploss = row["open"]
            #     candleType = "green rectangle"

            # red rectangle
            # if ((row["AROONOSC"] < aroonosc_min) and (row["high"] == row["open"]) and (row["low"] == row["close"])):  # downtrend
            #     orderType = "SELL"
            #     target = row["close"]
            #     stoploss = row["open"]
            #     candleType = "red rectangle"

            # nutral up doji
            # if ((row["AROONOSC"] > aroonosc_max) and (row["open"] == row["close"])):
            #     candleType = "nutral up doji"
            #     candle_upper = abs(row["high"]-row["close"])
            #     candle_lower = abs(row["open"]-row["low"])
            #     if(candle_upper < candle_lower):
            #         orderType = "BUY"
            #         target = row["high"]
            #         stoploss = row["low"]

            # nutral down doji
            # if ((row["AROONOSC"] < aroonosc_min) and (row["open"] == row["close"])):
            #     candleType = "nutral down doji"
            #     candle_upper = abs(row["high"]-row["close"])
            #     candle_lower = abs(row["open"]-row["low"])
            #     if(candle_upper > candle_lower):
            #         orderType = "SELL"
            #         target = row["low"]
            #         stoploss = row["high"]

            if(orderType == "BUY" or orderType == "SELL"):
                # RMS (risk management)
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
                if(total_price > margin):
                    qty = round((margin / price), 0)

                tradeWindow = abs(target - round(price, 1))
                if(tradeWindow == 0.05):
                    target = target + 0.05
                    # observe and work accordingly
                print(target)

                order = {
                    'candle': candleType,
                    'type': orderType,
                    'instrument': symbol,
                    'price': round(price, 1),
                    'qty': int(round(abs(qty))),
                    'target': target,
                    'stoploss': stoploss,
                    'volume': row["volume"],
                    'adx': row["ADX"],
                    'aroonosc': row["AROONOSC"],
                    'atr': row["ATR"],
                    'open': row['open'],
                    'high': row['high'],
                    'low': row['low'],
                    'close': row['close'],
                    'product': 'MIS',
                    'time': row["timestamp"],
                }


    if(circuit != 0):
        print("circuit : "+str(circuit) + "%  " + str(row["timestamp"]))
        print("adx : "+str(adx_now) + "  aroonosc : " + str(aroonosc_now))

    if(dayOpen != 0 and (circuit > upper_circuit_alert or circuit < lower_circuit_alert)):
        print("Trade Alert")

    if ((orderType != "") and (order["qty"] > 0) and (order["price"] < price_filter_max) and (order["price"] > price_filter_min) and (order["volume"] > volume_filter) and (datetime.now().hour < 15 or test_mod == "on") and (datetime.now().hour > 9 or test_mod == "on")):

        if(rpt != 0 and orderType != ""):
            print("rpt : "+str(rpt))

        order_time = (order["time"]).replace('+0530', '')
        timestamp = datetime.strptime(order_time, '%Y-%m-%dT%H:%M:%S')
        timestamp = str(timestamp.hour) + ":" + str(timestamp.minute)
        print(order)
        # windcard filter to escape lower and upper circuits
        # if(order["instrument"] != "symbol name to skip"):
        if((test_mod == "off")):
            order_validate(order, circuit_validation)

        if((test_mod == "on")):
            print("Test mod ON")

        orderType = ""
        candleType = ""
        circuit_validation = ""

    if((datetime.now().hour >= 15) or (datetime.now().hour < 10)):
        print("out of play time")

    print("-----------------------------------------------")
    return


def order_validate(order_data, circuit_validation):

    if((circuit_validation == "invalid")):
        log("Validation Failed : circuit range")
        return

    order_time = (order_data["time"]).replace('+0530', '')
    d1 = datetime.strptime(order_time, '%Y-%m-%dT%H:%M:%S')
    d2 = datetime.now()
    diff = round((d2-d1).total_seconds())
    headers = {'content-type': 'application/json',
               "authorization": kite_token}
    url = "https://kite.zerodha.com/oms/portfolio/positions"
    response = requests.get(url, timeout=600, headers=headers).json()
    check_order = "VALID"
    if(diff > min_candle_time and diff < max_candle_time and response["status"] == "success"):
        df_positions = pd.DataFrame(response["data"]["net"])
        for index, row in df_positions.iterrows():
            if(row["tradingsymbol"] == order_data["instrument"] and row["average_price"] > 0):
                check_order = "INVALID"

        if(check_order == "VALID"):
            log("Time Gap : "+str(diff))
            log("Validation : Success")
            order_generation(order_data)
        else:
            log("Validation Failed : Already Inplay")
            return

    else:
        log("Validation Failed : Time Gap in Seconds : "+str(diff))
        return


def order_generation(order_data):
    order = {
        "variety": "regular",
        "exchange": "NSE",
        "tradingsymbol": str(order_data["instrument"]),
        "transaction_type": str(order_data["type"]),
        "order_type": "MARKET",
        "quantity": order_data["qty"],
        "price": 0,
        "product": "MIS",
        "validity": "DAY",
        "disclosed_quantity": 0,
        "trigger_price": 0,
        "squareoff": 0,
        "stoploss": 0,
        "trailing_stoploss": 0,
        "user_id": "VM7727"
    }
    print(order)
    headers = {'content-type': 'application/x-www-form-urlencoded',
               "authorization": kite_token}
    log("TRADE LOCK")
    url = "https://kite.zerodha.com/oms/orders/regular"
    response = requests.post(
        url, timeout=600, headers=headers, data=order).json()

    if(response["status"] == "success" and int(response["data"]["order_id"]) > 0):

        price = getPrice(response["data"]["order_id"])
        if(price > 0):
            target_point = abs(order_data["price"]-order_data["target"])
            stoploss_point = abs(order_data["price"]-order_data["stoploss"])

            if(str(order_data["type"]) == "BUY"):
                if(price >= order_data["target"]):
                    order_data["target"] = round(price + (target_point/2), 1)
                if(price <= order_data["stoploss"]):
                    order_data["stoploss"] = round(price - (stoploss_point/2), 1)
                order_data["type"] = "SELL"
            else:
                if(price <= order_data["target"]):
                    order_data["target"] = round(price - (target_point/2), 1)
                if(price >= order_data["stoploss"]):
                    order_data["stoploss"] = round(price + (stoploss_point/2), 1)
                order_data["type"] = "BUY"

            stoploss(order_data)
            target(order_data)

    else:
        print(response)
    return


def getPrice(order_id):
    average_price = 0
    endpoint = "https://kite.zerodha.com/oms/orders"
    headers = {'content-type': 'application/json',
               "authorization": kite_token}
    url = endpoint
    response = requests.get(
        url, timeout=600, headers=headers).json()

    if(response["status"] == "success"):
        df_orders = pd.DataFrame(response["data"])
        for index, row in df_orders.iterrows():
            if(row["order_id"] == order_id and row["status"] == "COMPLETE"):
                average_price = row["average_price"]
    else:
        print(response)

    return average_price


def stoploss(order_data):
    order = {
        "variety": "regular",
        "exchange": "NSE",
        "tradingsymbol": str(order_data["instrument"]),
        "transaction_type": str(order_data["type"]),
        "order_type": "SL-M",
        "quantity": (int(order_data["qty"])),
        "price": 0,
        "product": "MIS",
        "validity": "DAY",
        "disclosed_quantity": 0,
        "trigger_price": order_data["stoploss"],
        "squareoff": 0,
        "stoploss": 0,
        "trailing_stoploss": 0,
        "user_id": "VM7727"
    }
    print(order)
    headers = {'content-type': 'application/x-www-form-urlencoded',
               "authorization": kite_token}
    url = "https://kite.zerodha.com/oms/orders/regular"
    response = requests.post(
        url, timeout=600, headers=headers, data=order).json()
    if(response["status"] == "success"):
        log("STOPLOSS LOCK")
    else:
        print(response)
    return


def target(order_data):
    order = {
        "variety": "regular",
        "exchange": "NSE",
        "tradingsymbol": str(order_data["instrument"]),
        "transaction_type": str(order_data["type"]),
        "order_type": "LIMIT",
        "quantity": order_data["qty"],
        "price":  order_data["target"],
        "product": "MIS",
        "validity": "DAY",
        "disclosed_quantity": 0,
        "trigger_price": 0,
        "squareoff": 0,
        "stoploss": 0,
        "trailing_stoploss": 0,
        "user_id": "VM7727"
    }
    print(order)
    headers = {'content-type': 'application/x-www-form-urlencoded',
               "authorization": kite_token}
    url = "https://kite.zerodha.com/oms/orders/regular"
    response = requests.post(
        url, timeout=600, headers=headers, data=order).json()
    if(response["status"] == "success"):
        log("TARGET LOCK")
    else:
        print(response)
    return


# -------------------------------------------------------------
scanning()

print("===================================================")
log("END")
print("===================================================")
end_time = datetime.now()
time_taken = divmod((end_time-start_time).total_seconds(), 60)[0]
print("Start Time     : "+str(start_time))
print("End Time       : "+str(end_time))
print("Time Taken     : "+str(time_taken))
print("===================================================")
