import os
import requests

from utils import formatNumber


api_key = os.environ['opensea_api_key']
headers = {"Accept": "application/json", "X-API-KEY": api_key}


def parse_floor(response):
    return formatNumber(response.json().get('stats').get('floor_price'))


def get_stats(collection):
    stats_url = f"https://api.opensea.io/api/v1/collection/{collection}/stats"
    response = requests.request("GET", stats_url, headers=headers)
    return response

def get_floor(collection):
    return parse_floor(get_stats(collection))

async def get_collection(collection):
    collection.replace(" ", "")
    url = F"https://api.opensea.io/api/v1/assets?collection={collection}&order_direction=desc&limit=20&include_orders=false"
    response = requests.get(url, headers=headers)

    assets = response.json().get('assets');
    asset_contract = assets[0].get('asset_contract');
    contract = asset_contract.get('address');
    image_url = asset_contract.get('image_url');
    description = asset_contract.get('description');
    external_link = asset_contract.get('external_link');
    
    return [contract, image_url, description, external_link]

def get_asset(contract, asset_id):
    asset_url = f"https://api.opensea.io/api/v1/asset/{contract}/{asset_id}/?include_orders=false"
    response = requests.request("GET", asset_url, headers=headers)
    return response
    