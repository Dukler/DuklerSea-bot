from utils import formatNumber
import requests


def get_eth_price():
    headers = {"Accept": "application/json"}
    ethPrice = parse_price(requests.request("GET", "https://api.coingecko.com/api/v3/coins/ethereum", headers=headers))
    return ethPrice


def parse_price(response):
    return formatNumber(response.json().get('market_data').get('current_price').get('usd'))
