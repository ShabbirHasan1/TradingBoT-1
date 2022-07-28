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

with open("token.json") as json_file:
    json_data = json.load(json_file)
    kite_token = json_data["kite_token"]


def positions(order_data_row, df_orders):
    tradingsymbol = order_data_row["tradingsymbol"]
    order_id = order_data_row["order_id"]
    order_status = order_data_row["status"]

    headers = {'content-type': 'application/json',
               "authorization": kite_token}
    url = "https://kite.zerodha.com/oms/portfolio/positions"
    response = requests.get(url, timeout=600, headers=headers).json()
    if(response["status"] == "success"):
        df_positions = pd.DataFrame(response["data"]["net"])
        for index, row in df_positions.iterrows():
            if(row["tradingsymbol"] == tradingsymbol and row["average_price"] == 0):
                print(tradingsymbol+" cancelling "+str(order_id))
                cancel_order(order_id)
    else:
        print(response)
    return


def cancel_order(order_id):
    print("-------------------")
    headers = {'content-type': 'application/json',
               "authorization": kite_token}
    url = "https://kite.zerodha.com/oms/orders/regular/" + \
        str(order_id)+"?order_id="+str(order_id) + \
        "&parent_order_id=&variety=regular"
    response = requests.delete(
        url, timeout=600, headers=headers).json()
    if(response["status"] == "success"):
        print("cancelled success")
    else:
        print(response)
    print("-------------------")


def cleaning():
    log("PROCESSING START")
    endpoint = "https://kite.zerodha.com/oms/orders"
    headers = {'content-type': 'application/json',
               "authorization": kite_token}
    url = endpoint
    response = requests.get(
        url, timeout=600, headers=headers).json()
    if(response["status"] == "success"):
        df_orders = pd.DataFrame(response["data"])
        for index, row in df_orders.iterrows():
            if(row["status"] == "TRIGGER PENDING" or row["status"] == "OPEN"):
                positions(row, df_orders)
    else:
        print(response)
    return


cleaning()

print("===================================================")
log("END")
print("===================================================")
end_time = datetime.now()
time_taken = divmod((end_time-start_time).total_seconds(), 60)[0]
print("Start Time     : "+str(start_time))
print("End Time       : "+str(end_time))
print("Time Taken     : "+str(time_taken))
print("===================================================")
