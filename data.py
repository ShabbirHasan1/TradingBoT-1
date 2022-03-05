#  https://api.kite.trade/instruments
# df = pd.read_csv('master/instruments')
# df1 = df.query(
#     ' instrument_type == "EQ" & segment == "NSE" & exchange == "NSE" & lot_size == 1 & name ')
# df2 = pd.DataFrame(df1, columns=['instrument_token', 'tradingsymbol'])
# # df2 = pd.DataFrame(df1)
# df2.to_csv("master/symbols")

import pandas as pd
from datetime import datetime
import requests
import pandas as pd
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

def scanning():
    total_data_points = 0
    log("PROCESSING INSTRUMENTS SYMBOLS")
    print("-----------------------------------------------")
    df_symbols = pd.read_csv('master/instruments.csv')
    # from_date = datetime.now().strftime('%Y-%m-%d')
    # to_date = datetime.now().strftime('%Y-%m-%d')
    from_date = "2022-03-04"
    to_date = "2022-03-04"
    for index, row in df_symbols.iterrows():
        endpoint = "https://kite.zerodha.com/oms/instruments/historical/"
        code = str(row["instrument_token"])
        # interval = "/5minute"
        interval = "/minute"
        headers = {'content-type': 'application/json',
                   "authorization": kite_token}
        url = endpoint + code + interval
        params = (
            ('user_id', 'VM7727'),
            ('oi', '1'),
            ('from', str(from_date)),
            ('to', str(to_date)),
        )
        response = requests.get(
            url, timeout=600, headers=headers, params=params).json()
        
        if(response['data']['candles'] and response["status"] == "success"):

            df = pd.DataFrame(response['data']['candles'], columns=[
                            'timestamp', 'open', 'high', 'low', 'close', 'volume', 'oi'])

            df.to_csv("data/"+row["tradingsymbol"]+".csv")

            if(df[df.columns[0]].count()):
                log(str(index)+" => "+str(df[df.columns[0]].count()) +
                    " DATA POINTS : "+row["tradingsymbol"])
        else:
            print("No data found")
    return


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
