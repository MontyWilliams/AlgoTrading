import json
import os
import requests
import eth_account
from eth_account.signers.local import LocalAccount
from hyperliquid.exchange import Exchange
from hyperliquid.info import Info
import subprocess

def setup(base_url='https://api.hyperliquid.xyz', skip_ws=False):
    config_path = os.path.join(os.path.dirname(__file__), 'config.json')
    with open(config_path) as f:
        config = json.load(f)
        account: LocalAccount = eth_account.Account.from_key(config["secret_key"])
        address =config["account_address"]
        if address == "":
            adress = account.address
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