import discord
from discord.ext import commands
from discord import app_commands
import os
from dotenv import load_dotenv
import asyncio
from discord.app_commands import Choice
import json
import aiohttp
import random
load_dotenv()
intents = discord.Intents.all()

client = commands.Bot(command_prefix='.', intents=intents)

ShopItems = {
    "Doonz Editions NFT - Claimable Ticket -" :(2000,"Your ticket to claim a NFT from Doonz NFT Editions Collections on OpenSea"),
    "Doonz NFT Airdrop - Claimable Ticket -" :(3000,"Your ticket to clain a Doonz NFT airdrop."),
    "Doonz Raffle Ticket" :(100,"Your ticked to join special raffles here on discord. **Please not that you will be granted the role after claiming this shop item and role will be removed after the raffle ends.**"), 
}

RoleMappedToReward = {
    1136242811004518490: 500,
    1136242648127123537:250,
    1123574209059237929:150,
    1136240524555194398: 30,
    1123573342738329650:10,
    1083474077282468021:20
}
#Fetching OpenSea
async def fetch_data():
    url = "https://api.opensea.io/api/v1/events?only_opensea=true&token_id=711&asset_contract_address=0x2ef45389859b6d3c99b789352121b2d250e3d5b0&collection_slug=doonz&event_type=transfer"

    headers = {
        "accept": "application/json",
        "X-API-KEY": "293ceb912ff74fccaa3c945bcc5c06bc"
    }

    async with aiohttp.ClientSession() as session:
        async with session.get(url, headers=headers) as response:
            if response.status == 200:
                data = await response.json()
                return data
            else:
                print(f"Failed to fetch data. Status code: {response.status}")
                return None


async def send_notification(event):
    embed = discord.Embed(
        title='New NFT Minted!',
        description=f'An NFT was minted in the collection: {event["collection"]["name"]}',
        color=discord.Color.green()
    )
    embed.add_field(name='Token ID', value=event['asset']['token_id'])
    embed.add_field(name='Seller', value=event['seller']['address'])
    embed.set_thumbnail(url=event['asset']['image_url'])
    MOKA = await client.fetch_user("368776198068895745")
    await MOKA.send(embed=embed)
    
async def getBankData():
    with open ("bank.json","r") as f:
        users = json.load(f)
    return users    
    
async def removeMoney(userid,value):
    users = await getBankData()
    users[userid]["balance"] -= value  
    with open ("bank.json","w") as f:
        json.dump(users,f)
        
async def addMoney(userid,value):
    users = await getBankData()
    users[userid]["balance"] += value  
    with open ("bank.json","w") as f:
        json.dump(users,f)
async def isUser(userid):
    users = await getBankData()
    if userid in users:
        return True
    return False

async def convert_seconds(seconds):
    hours = seconds // 3600
    minutes = (seconds % 3600) // 60
    seconds = seconds % 60

    return hours, minutes, seconds

async def holder(interaction: discord.Interaction):
  role = interaction.guild.get_role(1083474077282468021)
  if role in interaction.user.roles:
    return True
  await interaction.response.send_message(
    "<@{}> I am sorry only Doonz Holders can use me.".format(
      interaction.user.id),
    ephemeral=True)
  return False

async def owner(interaction: discord.Interaction):  # Me or Nash
    ownerRole = interaction.guild.get_role(1136244685116014684)
    modRole = interaction.guild.get_role(1138232772452941984) 
    if (ownerRole in interaction.user.roles) or (modRole in interaction.user.roles):
        return True
    await interaction.response.send_message(
    "<@{}> I am sorry only Admins can use me.".format(
      interaction.user.id),
    ephemeral=True)
    return False    
    
  
    
@client.event
async def on_ready():
    print('Doonz is running! Currently serving {0.user}'.format(client))
    await client.tree.sync()

cd_mapping = commands.CooldownMapping.from_cooldown(1, 120, commands.BucketType.user)
@client.event
async def on_message(message):
  bucket = cd_mapping.get_bucket(message)
  retry_after = bucket.update_rate_limit() 
  if not retry_after:   
    if message.author == client.user:
        return
    if message.author.bot:
        return
    validUser = await isUser(str(message.author.id))
    if validUser:
        await addMoney(str(message.author.id),random.randint(1, 5))




@client.tree.command(name="joindoonz", description="registering your account in Doonz's Discord eco system!")
async def joindoonz(interaction: discord.Interaction,matic_address: str,twitter_account: str):
    users = await getBankData()
    print(users)
    if str(interaction.user.id) in users:
        await interaction.response.send_message("You already have an account!",ephemeral=True)
        return False
    else:
        users[str(interaction.user.id)] = {"balance": 0, "WalletAddress": matic_address,"TwitterAccount":twitter_account}
        await interaction.response.send_message("Your account has been registered successfully!",ephemeral=True)
    with open ("bank.json","w") as f:
        json.dump(users,f)
    return True
            
@client.tree.command(name="balance", description="Checking your Doonz Coin Balance")
async def balance(interaction: discord.Interaction):
    try:
        users = await getBankData()
        UserBalance = users[str(interaction.user.id)]["balance"]
        em = discord.Embed(title=f"{interaction.user.name}'s Balance",color=discord.Color.yellow())
        em.add_field(name= "",value=f"Your current balance is: {UserBalance}")
        await interaction.response.send_message(embed=em,ephemeral=True)
    except:
        await interaction.response.send_message(content="Please create an account first by using `/joindoonz` command.",ephemeral=True)
        
        
@client.tree.command(name="edit_matic_wallet", description="Changes the matic wallet you saved in the eco bot")
async def edit_matic_wallet(interaction: discord.Interaction,matic_address: str): 
    validUser = await isUser((interaction.user.id))
    if validUser:
        users = await getBankData()
        users[str(interaction.user.id)]["WalletAddress"] = matic_address
        with open ("bank.json","w") as f:
            json.dump(users,f)
        await interaction.response.send_message(f"Your wallet address has been updated to `{matic_address}`.",ephemeral=True)
    else:
        await interaction.response.send_message(content="Please create an account first by using `/joindoonz` command.",ephemeral=True)
        
        
@client.tree.command(name="edit_twiiter_account", description="Changes the twitter account you saved in the eco bot")
async def edit_twiiter_account(interaction: discord.Interaction,twitter_acount: str): 
    validUser = await isUser((interaction.user.id))
    if validUser:
        users = await getBankData()
        users[str(interaction.user.id)]["TwitterAccount"] = twitter_acount
        with open ("bank.json","w") as f:
            json.dump(users,f)
        await interaction.response.send_message(f"Your wallet address has been updated to `{twitter_acount}`.",ephemeral=True)
    else:
        await interaction.response.send_message(content="Please create an account first by using `/joindoonz` command.",ephemeral=True)
        
        
@client.tree.command(name="shop", description="Preview all items in shop")
async def shop(interaction: discord.Interaction):
    em = discord.Embed(title="Doonz Shop",color=discord.Color.yellow())
    for key,value in ShopItems.items():
        em.add_field(name= f"{key} - {value[0]} :moneybag:",value=value[1],inline=False) 
    await interaction.response.send_message(embed=em,ephemeral=True)
        

def loadShopChoices():
    ls = []
    for key,value in ShopItems.items():
        ls.append(Choice(name=key, value=value[0]))
    return ls
        

    
@client.tree.command(name="buy_item", description="To purchase items from the shop")
@app_commands.choices(
    shop_item =  loadShopChoices()
)
async def buy_item(interaction: discord.Interaction,shop_item: Choice[int]):
    # Reading user balance
    users = await getBankData()
    UserBalance = users[str(interaction.user.id)]["balance"]
    if UserBalance < shop_item.value:
        await interaction.response.send_message("You don't have enough coins!",ephemeral=True)
    else:
        if(shop_item.name == "Doonz Raffle Ticket"): # Add role logic
            RaffleRole = discord.utils.get(interaction.guild.roles, name="Raffle Ticket")
            if RaffleRole in interaction.user.roles:
                await interaction.response.send_message("You already have this role!",ephemeral=True)
                return
            await interaction.user.add_roles(RaffleRole)
            await interaction.response.send_message(f"**Raffle Ticket** role has been added. Good luck in the raffle!")
        else:
            await interaction.response.send_message(f"{shop_item.name} has been purchased, please open a <#1124318043355480115> to claim it!")   
        await removeMoney(str(interaction.user.id),shop_item.value)
        
            
            
              
@client.tree.command(name="leaderboard", description="Displays the leaderboard!")
async def leaderboard(interaction: discord.Interaction):
    users = await getBankData()
    em = discord.Embed(title="Doonz Coin Leaderboard",color=discord.Color.yellow())
    Leaderboard = []
    for user in users:
        Leaderboard.append((users[user]["balance"],user))
    Leaderboard.sort(key=lambda tup: tup[0])
    for i in range(10):
        if i < len(Leaderboard):
            em.add_field(name="",value=f"{i+1}- <@{Leaderboard[i][1]}> ({Leaderboard[i][0]})")
    await interaction.response.send_message(embed=em)

@client.tree.command(name="add_money", description="adds money to a user")
@commands.check(owner)
async def add_money(interaction: discord.Interaction,send_to:discord.User,amount: str):
    await addMoney(str(send_to.id),int(amount))
    em = discord.Embed(title="Doonz Coin Leaderboard",color=discord.Color.yellow())
    em.add_field(name="",value=f"added {amount} :moneybag: to <@{interaction.user.id}>")
    await interaction.response.send_message(embed=em)
 

    
    
                
@client.tree.command(name="dailycoins", description="Collect daily coins")
@commands.check(holder)
@app_commands.checks.cooldown(1, 86400.0, key=lambda i: (i.user.id))
async def dailycoins(interaction: discord.Interaction):
    users = await getBankData()
    validUser = await isUser(str(interaction.user.id))
    if not validUser:
        interaction.response.send_message("Please create an account using the /joindoonz command",ephemeral=True)
        return
    for role in RoleMappedToReward:
        DesiredRole = interaction.guild.get_role(role)
        if DesiredRole in interaction.user.roles:
            await addMoney(str(interaction.user.id),RoleMappedToReward[role])
            em = discord.Embed(title="Daily Doonz Coins",color=discord.Color.yellow())
            em.add_field(name="",value=f"You claimed your daily {RoleMappedToReward[role]} Doonz Coinz for your <@{role}> role.",inline=False)
            em.add_field(name="",value="Come back tommorow for more coinz or be active in the community or lucky in giveaways.:moneybag:",inline=False)
            await interaction.response.send_message(embed=em)
            return
    
        
@dailycoins.error
async def on_test_error(interaction: discord.Interaction,error: app_commands.AppCommandError):
   if isinstance(error, app_commands.CommandOnCooldown):
     RemainingHours,RemainingMin,RemainingSec = await convert_seconds(error.retry_after)
     await interaction.response.send_message("Please wait for {} hours, {} minutes, {} seconds.".format(
       int(RemainingHours),int(RemainingMin),int(RemainingSec)),ephemeral=True)   

    





client.run(os.getenv('TOKEN'))
