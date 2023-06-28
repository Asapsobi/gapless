import requests
import time
import hmac
import hashlib
import json
import urllib

api_key = 'mx0vgl1BaWS4A69jqa'
api_secret = '72b60bd2db254da78f6c3a28f5bdc099'
secret_key = b'72b60bd2db254da78f6c3a28f5bdc099'

avr_asks =[0,0,0,0,0]
avr_bids =[0,0,0,0,0]
def price_order () :
    url = "https://api.mexc.com/api/v3/depth"
    params = {"symbol": "USDDUSDC"}
    response = requests.get(url, params=params)

    # Extracting the bids list from the response JSON
    bids = response.json()["bids"]
    asks = response.json()["asks"]

    # Printing only the bid prices
    bid_order_prices = [round(float(bid[0])+0.0001, 4) for bid in bids]

    bid_order_prices1=(bid_order_prices[0])
    
    average_bids= sum (bid_order_prices[:5])/ 5


    # Printing only the first 5 ask prices
    ask_order_prices = [round(float(ask[0])-0.0001, 4) for ask in asks ]
   
    ask_order_prices1=ask_order_prices[0]
   
   
    average_asks= sum (ask_order_prices[:5])/ 5


    return ask_order_prices1 ,bid_order_prices1 , average_bids , average_asks 


ask_order_prices1 ,bid_order_prices1 , average_bids , average_asks = price_order()


# Endpoint parameters
def order() :
    params = {
        'symbol': 'USDDUSDC',
        'timestamp': int(time.time() * 1000),
        'recvWindow': 60000
    }

    # Build totalParams as the query string concatenated with the request body
    query_string = urllib.parse.urlencode(params)
    total_params = f"{query_string}"

    # Hash the totalParams using HMAC SHA256
    signature = hmac.new(secret_key, total_params.encode('utf-8'), hashlib.sha256).hexdigest()

    # Send request to signed endpoint
    url = 'https://api.mexc.com/api/v3/openOrders'
    headers = {'X-MEXC-APIKEY': api_key}
    params['signature'] = signature

    response = requests.get(url, headers=headers, params=params)
    response = response.content

    data = json.loads(response.decode('utf-8'))
    OrderList=[]
    for item in data:
        origQty=(item['origQty'])
        orderPrice=(item['price'])
        orderId=(item['orderId'])
        orderIdXQty=[orderId,origQty,orderPrice]
        OrderList.append(orderIdXQty)
        
    
    return OrderList

OrderList = order()


def IsCancel(OrderList,bid_order_prices,ask_order_prices) :
    cancelList=[]
    for order in OrderList :
        if order[2] == bid_order_prices :
            continue
        elif order[2] == ask_order_prices :
            continue
        else :
            print("order" , order[0] , "be qeymate" ,order[1] , "chon barabar" , bid_order_prices , ask_order_prices , "nist bayad delete she"   )
            cancelList.append(order[0])

    return (cancelList)

cancelList=IsCancel(OrderList,bid_order_prices1,ask_order_prices1)


def del_orders(order_id):
    params = {
        'symbol': 'USDDUSDC',
        'orderId': order_id,
        'timestamp': int(time.time() * 1000),
        'recvWindow': 60000

    }

    # Build totalParams as the query string concatenated with the request body
    query_string = urllib.parse.urlencode(params)
    total_params = f"{query_string}"

    # Hash the totalParams using HMAC SHA256
    signature = hmac.new(secret_key, total_params.encode('utf-8'), hashlib.sha256).hexdigest()

    # Send request to signed endpoint
    url = f'https://api.mexc.com/api/v3/order?{total_params}&signature={signature}'
    headers = {'X-MEXC-APIKEY': api_key}

    response = requests.delete(url, headers=headers)
    response_json = response.json()

    return response_json

def ordercanceling(cancelList) :
    for order in cancelList :
        order_id = order 
        del_orders(order_id)


def ordering_ask_order( ) :

    endpoint = 'https://api.mexc.com/api/v3/order'

    params = {
        'symbol': 'USDDUSDC',
        'side': 'SELL',
        'type': 'LIMIT',
        'quantity': 10,
        'price': ask_order_prices1,
        'recvWindow': 60000,
        'timestamp': int(time.time() * 1000)
    }


    # Create the message for signing
    message = '&'.join([f'{k}={v}' for k, v in params.items()])
    signature = hmac.new(api_secret.encode(), message.encode(), hashlib.sha256).hexdigest()

    # Add the signature to the request headers
    headers = {'X-MEXC-APIKEY': api_key}
    payload = {**params, 'signature': signature}

    # Send the request
    response = requests.post(endpoint, headers=headers, data=payload)
    print(response.json())

def ordering_bid_order() :

    endpoint = 'https://api.mexc.com/api/v3/order'
    print (bid_order_prices1)
    params = {
        'symbol': 'USDDUSDC',
        'side': 'BUY',
        'type': 'LIMIT',
        'quantity': 10,
        'price': bid_order_prices1,
        'recvWindow': 60000,
        'timestamp': int(time.time() * 1000)
    }


    # Create the message for signing
    message = '&'.join([f'{k}={v}' for k, v in params.items()])
    signature = hmac.new(api_secret.encode(), message.encode(), hashlib.sha256).hexdigest()

    # Add the signature to the request headers
    headers = {'X-MEXC-APIKEY': api_key}
    payload = {**params, 'signature': signature}

    # Send the request
    response = requests.post(endpoint, headers=headers, data=payload)
    print(response.json())


while 1>0 :
    
    ask_order_prices1 ,bid_order_prices1 , average_bids , average_asks = price_order()
    if ask_order_prices1 > 1 :
        ordering_ask_order()
    else : print("nemisarfe dadash")

    if bid_order_prices1 < 1 :
        ordering_bid_order()
    else : print("nemisarfe dadash")

    OrderList = order()
    cancelList=IsCancel(OrderList,bid_order_prices1,ask_order_prices1)
    ordercanceling(cancelList)
    print("i orderd in" , ask_order_prices1 ,bid_order_prices1 , "\n my orders are:" , OrderList , "\n my cancel iste are" , cancelList )
