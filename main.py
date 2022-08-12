import asyncio
import os

import discord
import math
from CoinGeckoAPI import get_eth_price
from OpenSeaAPI import get_asset, get_collection, get_floor
from discord import app_commands
import requests


intents = discord.Intents.all()

client = discord.Client(intents=intents)
bot = app_commands.CommandTree(client)

collection = "wagmiarmy"
cmd= "wagmi"
contract = "0xc86664e7d2608f881f796ee8e24fa9d4d7598406"
stats_url = f"https://api.opensea.io/api/v1/collection/{collection}/stats"


async def set_collection(_name, _contract, _nick,image_url):
    global collection, contract, cmd
    collection = _name
    cmd = _nick
    contract = _contract
    await client.change_presence(status=discord.Status.online, activity=discord.Activity(type=discord.ActivityType.watching, name=f'{_name} collection'))
    response = requests.get(image_url)
    await client.user.edit(avatar=response.content)

def get_os_url(asset_id):
    return f"https://opensea.io/assets/ethereum/{contract}/{asset_id}"


def get_traits(response, embed):
    nl = '\n'
    traits = response.json().get('traits')
    traits_string = ''
    index = 0
    for trait in traits:
        trait_list = response.json().get('traits')
        type = trait_list[index].get('trait_type')
        value = trait_list[index].get('value')
        count = trait_list[index].get('trait_count')
        trait_rarity = math.ceil(round(count / 100, 2))
        trait_desc = f'{value} {nl} ({trait_rarity}%)'
        index += 1
        embed.add_field(name=type, value=trait_desc, inline=True)
        traits_string = traits_string + type + ': ' + value + ', ' 
    return traits_string[:-2] + '.'

@bot.command(name='floor')
async def on_message(ctx):
    message = ctx.message
    if message.author:
        ethPrice = get_eth_price()
        floor_price = get_floor(collection)
        answer = "{name} floor: {eth} ETH ${usd}".format(name=cmd, eth=floor_price, usd=round(ethPrice*floor_price,2))
        await message.channel.send(answer)
            


async def get_nft(interaction:discord.Interaction, asset_id:str):
    response = get_asset(contract, asset_id)
    image = response.json().get('image_url')
    embedVar = discord.Embed(title=f"{cmd} #{asset_id}", description="",url=get_os_url(asset_id), color=0x00ff00)
    embedVar.set_image(url=image)
    traits = get_traits(response,embedVar)
    # return embedVar
    await interaction.response.send_message(embed=embedVar)


@bot.command(name='asset', description='get specific asset description')
async def send_asset_embed(interaction:discord.Interaction, asset_id:str):
    await get_nft(interaction,asset_id)

def collection_embed(collection,description,image_url):
    url = f"https://opensea.io/collection/{collection}"
    embedVar = discord.Embed(title=collection, description=description,url=url, color=0x00ff00)
    embedVar.set_image(url=image_url)
    embedVar.add_field(name='Contract', value=contract)
    return embedVar

class Confirmation(discord.ui.View):
    collection = ''
    contract = ''
    new_command = ''
    image_url = ''
    def set_col(self, collection, contract, new_command,image_url):
        self.collection = collection
        self.contract = contract
        self.new_command = new_command
        self.image_url = image_url
    @discord.ui.button(label='No', style=discord.ButtonStyle.red,custom_id='no')
    async def No(self, interaction: discord.Interaction, button: discord.ui.Button):
        print(button)

    @discord.ui.button(label='Yes', style=discord.ButtonStyle.green,custom_id='yes')
    async def Yes(self, interaction: discord.Interaction, button: discord.ui.Button):
        await set_collection(self.collection, self.contract, self.new_command,self.image_url)
        await interaction.response.edit_message(view=self)

    # async def interaction_check(self, interaction: discord.Interaction) -> bool:
    #     print('intercheck')
    #     print(self.id)
    #     if self.id == 'yes':
    #         print('sisisisi')
    #         return True
    #     return True
    


class Modal(discord.ui.Modal, title='Commands configuration'):
    collection_name = discord.ui.TextInput(label="Collection name", style=discord.TextStyle.short, placeholder='cryptopunks', required= True)
    # new_command = discord.ui.TextInput(label="Lowercase new command", style=discord.TextStyle.short, placeholder='cryptopunk', required= True, default='cryptopunk')
    async def on_submit(self, interaction: discord.Interaction):
        col = str(self.collection_name)
        cmd = 'asset'
        [contract, image_url, description, external_link] = await get_collection(col)
        view = Confirmation(timeout=None)
        view.set_col(col,contract,cmd,image_url)
        embedVar = collection_embed(col,description,image_url)
        await interaction.response.send_message(content='Is this the collection?', embed=embedVar, view=view, ephemeral=True)
        


@bot.command(name='set_collection', description='Sets the bot to a new collection')
async def self(interaction:discord.Interaction):
    modal = Modal()
    await interaction.response.send_modal(modal)
 

@client.event
async def on_ready():
    await bot.sync()
    [contract, image_url, description, external_link] = await get_collection(collection)
    await set_collection(collection,contract,cmd,image_url)
    print('ready')




async def main():
    await client.start(os.environ['discord_api_key'])


if __name__ == "__main__":
    asyncio.run(main())

