from typing import Optional
import discord
from discord.ext import commands,tasks
from discord import app_commands
import os
from dotenv import load_dotenv
import asyncio
from discord.ui import Button
import datetime
from discord.app_commands import Choice
import json
import aiohttp
import re
import random
ShopItems = {
    "DOONZ NFT AIRDROP🎈" :(30000,"Your ticket to claim a Doonz NFT airdrop."),
    "DOONZ EDITIONS NFT 🎨 " :(20000,"Your ticket to claim a Doonz Editions NFT."),
    "RAFFLE TICKET 🎟️" :(1000,"Your ticket to join special raffles here on discord. **Please not that you will be granted the role after claiming this shop item and role will be removed after the raffle ends.**"), 
}





    
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
  role = interaction.guild.get_role(1123573342738329650)
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
    
class SimpleView(discord.ui.View):
    
        
    def __init__(self, timeout=None):
        super().__init__(timeout=timeout)
        self.role = None
        self.ListofPeople = []
        self.em = None
        self.message = None
        
        
    @discord.ui.button(label="Enter Giveaway")
    async def GiveAway(self,interaction: discord.Interaction,button:discord.ui.Button):
        if not (self.role in interaction.user.roles):
            await interaction.response.send_message(f"I am sorry, only people with <@&{self.role.id}> can join.",ephemeral=True)
            
        if interaction.user in self.ListofPeople:
            await interaction.response.send_message("You have already joined this giveaway!",ephemeral=True)
        else:
            await interaction.response.send_message("You have joined this giveaway!",ephemeral=True)
            self.ListofPeople.append(interaction.user)
            self.em.set_field_at(4,name="",value= f":large_blue_diamond: Number of Participants: {str(len(self.ListofPeople))}",inline= False)
            await self.message.edit_original_response(embed=self.em,view=self)
            

async def CreateAccount(userid,matic,twitter):
    users = await getBankData()
    users[userid] = {"balance": 0, "WalletAddress": matic,"TwitterAccount":twitter}
    with open ("bank.json","w") as f:
        json.dump(users,f)    

          
          
          
class StartCog(commands.Cog):
    def __init__(self,client):
        self.client = client
            
            
        
    @app_commands.command(name="user_info", description="Displays user's info")
    async def user_info(self,interaction: discord.Interaction,user: discord.User): 
        validuser = await isUser(str(user.id))
        if validuser:
            users = await getBankData()
            em = discord.Embed(title=f"{user.name}'s Info",color= discord.Color.yellow())
            Balance = users[str(user.id)]["balance"]
            Address = users[str(user.id)]["WalletAddress"]
            Twiiter = users[str(user.id)]["TwitterAccount"]
            em.add_field(name="",value=f"User's Balance: {Balance}",inline=False)
            em.add_field(name="",value=f"User's ETH Address: {Address}",inline=False)
            em.add_field(name="",value=f"User's Twiiter Account: {Twiiter}",inline=False)
            await interaction.response.send_message(embed=em)
        else:
            await interaction.response.send_message("This user isn't registered in our system",ephemeral=True)
        
        
                
    @app_commands.command(name="edit_matic_wallet", description="Changes the matic wallet you saved in the eco bot")
    async def edit_matic_wallet(self,interaction: discord.Interaction,matic_address: str): 
        validUser = await isUser(str(interaction.user.id))
        if validUser:
            users = await getBankData()
            users[str(interaction.user.id)]["WalletAddress"] = matic_address
            with open ("bank.json","w") as f:
                json.dump(users,f)
            await interaction.response.send_message(f"Your wallet address has been updated to `{matic_address}`.",ephemeral=True)
        else:
            await interaction.response.send_message(content="Please create an account first by using `/joindoonz` command.",ephemeral=True)
            
            
    @app_commands.command(name="edit_twiiter_account", description="Changes the twitter account you saved in the eco bot")
    async def edit_twiiter_account(self,interaction: discord.Interaction,twitter_acount: str): 
        validUser = await isUser(str(interaction.user.id))
        if validUser:
            users = await getBankData()
            users[str(interaction.user.id)]["TwitterAccount"] = twitter_acount
            with open ("bank.json","w") as f:
                json.dump(users,f)
            await interaction.response.send_message(f"Your wallet address has been updated to `{twitter_acount}`.",ephemeral=True)
        else:
            await interaction.response.send_message(content="Please create an account first by using `/joindoonz` command.",ephemeral=True)
            
            
    @app_commands.command(name="shop", description="Preview all items in shop")
    async def shop(self,interaction: discord.Interaction):
        em = discord.Embed(title="🛒COINZ SHOP🛒",color=discord.Color.yellow())
        for key,value in ShopItems.items():
            em.add_field(name= f" {key} \nPrice: {value[0]} Doonz Coinz :moneybag:",value=value[1],inline=False) 
        await interaction.response.send_message(embed=em,ephemeral=True)
            

    def loadShopChoices():
        ls = []
        for key,value in ShopItems.items():
            ls.append(Choice(name=key, value=value[0]))
        return ls
            

        
    @app_commands.command(name="buy_item", description="To purchase items from the shop")
    @app_commands.choices(
        shop_item =  loadShopChoices()
    )
    async def buy_item(self,interaction: discord.Interaction,shop_item: Choice[int]):
        # Reading user balance
        users = await getBankData()
        UserBalance = users[str(interaction.user.id)]["balance"]
        if UserBalance < shop_item.value:
            await interaction.response.send_message("You don't have enough coinz!",ephemeral=True)
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
            
                
                
                
    @app_commands.command(name="leaderboard", description="Displays the leaderboard!")
    async def leaderboard(self,interaction: discord.Interaction):
        users = await getBankData()
        em = discord.Embed(title="Doonz Coin Leaderboard",color=discord.Color.yellow())
        Leaderboard = []
        for user in users:
            Leaderboard.append((users[user]["balance"],user))
        Leaderboard.sort(key=lambda tup: tup[0],reverse=True)
        for i, entry in enumerate(Leaderboard[:10], start=1):
            em.add_field(name="", value=f"{i}- <@{entry[1]}> ({entry[0]})",inline=False)
        await interaction.response.send_message(embed=em)

    @app_commands.command(name="add_money", description="adds money to a user")
    @commands.check(owner)
    async def add_money(self,interaction: discord.Interaction,send_to:discord.User,amount: str):
        await addMoney(str(send_to.id),int(amount))
        em = discord.Embed(title="Doonz Coin Leaderboard",color=discord.Color.yellow())
        em.add_field(name="",value=f"added {amount} :moneybag: to <@{send_to.id}>")
        await interaction.response.send_message(embed=em)
    



async def setup(client:commands.Bot) -> None:
    await client.add_cog(StartCog(client))