import json
import os
import time
import requests
import eth_account
from eth_account.signers.local import LocalAccount
from eth_account import Account
from hyperliquid.exchange import Exchange
from hyperliquid.info import Info
import subprocess
from pprint import pprint
from decimal import Decimal
from eth_account.messages import encode_defunct

def setup(base_url='https://api.hyperliquid.xyz', skip_ws=False):
    config_path = os.path.join(os.path.dirname(__file__), 'config.json')
    with open(config_path) as f:
        config = json.load(f)
        account: LocalAccount = eth_account.Account.from_key(config["secret_key"])
        address =config["account_address"]
        if address == "":
            address = account.address
        # print("Running with account address:", address)
        if address != account.address:
            # print("Running with agent address:", account.address)
            print("Running setup")
        info = Info(base_url, skip_ws)
        user_state = info.user_state(address)
        spot_user_state = info.spot_user_state(address)
        margin_summary = user_state["marginSummary"]
        if float(margin_summary["accountValue"]) == 0 and len(spot_user_state["balances"]) == 0:
            print("Account value is 0, please fund your account")
            url = info.base_url.split(".", 1)[1]
            error_string = f"No accountValue:\nIf you think this is a mistake, make sure that {address} has a balance on {url}.\nIf address shown is your API wallet address, update the config to specify the address of your account, not the address of the API wallet."
            raise Exception(error_string)
        exchange = Exchange(account, base_url, account_address=address)
        return address, info, exchange, account

def setup_multi_sig_wallets():


    
    config_path = os.path.join(os.path.dirname(__file__), "config.json")
    with open(config_path) as f:
        config = json.load(f)

    authorized_user_wallets = []
    for wallet_config in config["multi_sig"]["authorized_users"]:
        account: LocalAccount = eth_account.Account.from_key(wallet_config["secret_key"])
        address = wallet_config["account_address"]
        if account.address != address:
            raise Exception(f"provided authorized user address {address} does not match private key")
        print("loaded authorized user for multi-sig", address)
        authorized_user_wallets.append(account)
    return authorized_user_wallets

def ask_bid(symbol):
    """
    This function returns the ask and bid price for the given symbol
    """
    url = 'https://api.hyperliquid.xyz/info'
    headers = {'Content-Type': 'application/json'}
    
    data = {
        'type': 'l2Book',
        'coin': symbol,
    }

    response = requests.post(url, headers=headers, data=json.dumps(data))
    l2_data = response.json()
    l2_data = l2_data['levels']

    bid = float(l2_data[0][0]['px'])
    ask = float(l2_data[1][0]['px'])

    return ask, bid, l2_data

def get_sz_px_decimals(symbol):
    """
    This returns a tuple size decmals and price
    decimals for the given coin
    """
    url = 'https://api.hyperliquid.xyz/info'
    headers = {'Content-Type': 'application/json'}
    data = {'type': 'meta'}

    response = requests.post(url, headers=headers, data=json.dumps(data))
    if response.status_code == 200:
        data = response.json()
        symbols = data['universe']
        symbol_info = next((s for s in symbols if s['name'] == symbol), None)
        if symbol_info:
            sz_decimals = symbol_info['szDecimals']
        else:
            print('symbol not found')
    else:
        print('Error:', response.status_code, response.text)
    
    ask = ask_bid(symbol)[0]

    ask_str = str(ask)
    if '.' in ask_str:
        px_decimals = len(ask_str.split('.')[1])
    else:
        px_decimals = 0
    
    print(f'{symbol} at price {sz_decimals} decimals')

    return sz_decimals, px_decimals

def play_sound(file_path):
    """
    Play a sound file using ffplay.
    """
    if not os.path.exists(file_path):
        print(f"Error: Sound file '{file_path}' not found.")
        return

    try:
        subprocess.run(
            ["ffplay", "-nodisp", "-autoexit", file_path],
            stdout=subprocess.DEVNULL,  # Suppress standard output
            stderr=subprocess.DEVNULL   # Suppress error output
        )
    except FileNotFoundError:
        print("Error: 'ffplay' is not installed or not found in PATH.")

def get_symbol_index(symbol):
    """
    Gets data from Univers and returns index of symbol
    """
    url = "https://api.hyperliquid.xyz/info"
    headers = {"Content-Type": "application/json"}
    data = { "type": "meta" }

    response = requests.post(url, headers=headers, json=data)
    if response.status_code == 200:
        # with open("meta_output.json", "w") as f:
        #     json.dump(response.json(), f, indent=4)
        data = response.json()
        universe = data["universe"]
        symbol_index = None
        for index, asset in enumerate(universe):
            if asset.get("name") == symbol:
                symbol_index = index
                break
        if symbol_index:
            print(f"Symbol '{symbol}' found at index {symbol_index}.")
        else:
            print(f"Symbol '{symbol}' not found in the universe.")

    else:
        print("error")

    return symbol_index

def get_user_orders(address, info):
    """
    Gets all open orders and returns them as a dict along with a bool
    """
    user_state = info.user_state(address)
    open_positions = user_state["assetPositions"]
    # pprint(user_state)
    
    result = []
    for position in open_positions:
        szi = float(position["position"]["szi"])
        if szi == 0:
            continue
        symbol = position["position"]["coin"]
        index_pos = get_symbol_index(symbol)
        long = szi > 0
        entry_price = position["position"]["entryPx"]
        leverage = position["position"]["leverage"]["value"]
        pnl = position["position"]["unrealizedPnl"]
        result.append({
            "symbol": symbol,
            "size": abs(szi),
            "long": long,
            "index_pos": index_pos,
            "entry_price": entry_price,
            "leverage": leverage,
            "pnl": pnl
        })
    if position:
        return result, True
    else:
        print("No open positions found.")
        return result, False

def cancel_open_orders(address, info, exchange):
    """
    Finds open orders and cancels them if they exist.
    """
    
    open_orders = info.open_orders(address)
    if not open_orders:
        print("No open orders to cancel.")
        return
    else:
        for open_order in open_orders:
            print("Found open order. Cancelling...")
            exchange.cancel(open_order["coin"], open_order["oid"])
            updated_open_orders = info.open_orders(address)
            if any(order["oid"] == open_order["oid"] for order in updated_open_orders):
                print(f"Cancellation failed. Order {open_order['oid']} still exists.")
            else:
                print(f"Successfully cancelled order {open_order['oid']} for coin {open_order['coin']}.")

def get_candles(symbol, timeframe, limit):
    """"
    - Get candles for a given symbol, timeframe/limit
    - Returns a dict of candles
    """
    timeframe = int(timeframe)  # Convert to int incase it is a string
    end_time = int(time.time() * 1000)  # Current time in milliseconds
    interval_miliseconds = timeframe * 60 * 1000    # Convert timeframe to milliseconds
    start_time = end_time - (limit * interval_miliseconds)  # Calculate start time
    url = " https://api.hyperliquid.xyz/info"
    headers = {"Content-Type": "application/json"}
    data = {
        "type": "candleSnapshot",
        "req": {
            "coin": symbol,
            "interval": f"{timeframe}m",  # Format interval as a string with 'm' of api will refuse
            "startTime": start_time,
            "endTime": end_time,
        }
    }

    response = requests.post(url, headers=headers, json=data)
    if response.status_code == 200:
        candles = response.json()
        candle_sticks = []
        for candle in candles:
            open = float(candle["o"])
            close = float(candle["c"])
            high = float(candle["h"])
            low = float(candle["l"])
            timestamp = candle["t"]
            volume = float(candle["v"])
            symbol = candle["s"]
            candle_sticks.append({
                "open": open,
                "close": close,
                "high": high,
                "low": low,
                "timestamp": timestamp,
                "volume": volume,
                "symbol": symbol
            })
        return candle_sticks
    else:
        print("Error: .....", response.status_code, response.text)
        return None
    