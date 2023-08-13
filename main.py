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
from cogs.cog1 import *
load_dotenv()
intents = discord.Intents.all()

class Client(commands.Bot):
    def __init__(self):
        super().__init__(command_prefix=commands.when_mentioned_or('.'), intents=intents)
    
    async def setup_hook(self):
        await self.load_extension("cogs.cog1")
    
    async def on_ready(self):
        print('Doonz is running! Currently serving {0.user}'.format(client))
        await self.tree.sync()
    


RoleMappedToReward = {
    1136242811004518490: 500, 
    1136242648127123537:250,
    1123574209059237929:100,
    1136240934632312983:50,
    1136240524555194398: 30,
    1123573342738329650:10, 
}

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

async def holder(interaction: discord.Interaction):
  role = interaction.guild.get_role(1123573342738329650)
  if role in interaction.user.roles:
    return True
  await interaction.response.send_message(
    "<@{}> I am sorry only Doonz Holders can use me.".format(
      interaction.user.id),
    ephemeral=True)
  return False     

client = Client()
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
async def joindoonz(interaction: discord.Interaction,matic_address: str = "",twitter_account: str = ""):
    users = await getBankData()
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
        users = await getBankData()
        UserBalance = users[str(interaction.user.id)]["balance"]
        em = discord.Embed(title=f"{interaction.user.name}'s Balance",color=discord.Color.yellow())
        em.add_field(name= "",value=f"Your current balance is: {UserBalance}")
        validUser = await isUser(str(interaction.user.id))
        if validUser:
            await interaction.response.send_message(embed=em,ephemeral=True)
        else:    
            await interaction.response.send_message(content="Please create an account first by using `/joindoonz` command.",ephemeral=True)
        

async def generategiveaway(interaction: discord.Interaction,giveaway_minutes: int,prize: str,winners: int,role_limit: discord.Role):

    view = SimpleView(timeout=giveaway_minutes *60)
    view.role = role_limit
    em = discord.Embed(title=prize,color=discord.Color.yellow())
    em.add_field(name="",value=f":large_blue_diamond: Hosted By: <@{interaction.user.id}>",inline=False)
    EndTime = datetime.datetime.now() + datetime.timedelta(seconds= giveaway_minutes*60 )
    DisplayedTime = EndTime.timestamp()
    em.add_field(name="",value= f":large_blue_diamond: Allowed Role: <@&{role_limit.id}>",inline=False)
    em.add_field(name="",value= f":large_blue_diamond: Ends At: {discord.utils.format_dt(datetime.datetime.fromtimestamp(DisplayedTime), 'R')}",inline=False)
    em.add_field(name="",value= f":large_blue_diamond: Number of Winners: {winners}",inline=False)
    em.add_field(name="",value= f":large_blue_diamond: Number of Participants: {str(0)}",inline=False)
    view.em = em
    GiveAwayMessage = await interaction.response.send_message(embed=em,view=view)
    view.message = interaction
    await asyncio.sleep(giveaway_minutes * 60)
    for i in view.children:
        i.disabled = True
    await interaction.edit_original_response(embed=em,view=view) #Disables the button
    WinnerList = []
    if len(view.ListofPeople) == 0:
        await interaction.followup.send("Oh no, it seems like no one joined the giveaway :(")
        return
    for i in range(winners):
        if winners - i >= len(view.ListofPeople): # 3 winners 2 participants 
            Winner = random.choice(view.ListofPeople)
            WinnerList.append(Winner)
            view.ListofPeople.pop(view.ListofPeople.index(Winner))
        else:
            break
    if len(WinnerList):
        StringOfWinners = ""
        for winner in WinnerList:
            winmention = "<@" + str(winner.id) + ">"
            StringOfWinners += winmention

            
        await interaction.followup.send(f"Congratulations to {StringOfWinners}!")
        return StringOfWinners
            
@client.tree.command(name="create_giveaway", description="Creates a giveaway!")
@commands.check(owner)
async def create_giveaway(interaction: discord.Interaction,giveaway_minutes: int,prize: str,winners: int,role_limit: discord.Role):
    await generategiveaway(interaction,giveaway_minutes,prize,winners,role_limit)
        
        


HelperDec = {0:"Head",
                1:"Tail"}
@client.tree.command(name="headsortails", description="If you win it gives you double the amount you bet, if you lose you lose your bet :( MAXIMUM BET: 100")
@app_commands.choices(
    choice =  [Choice(name="Head", value=0),Choice(name="Tail",value=0)]
)
@commands.check(holder)
@app_commands.checks.cooldown(2, 10*60, key=lambda i: (i.user.id))
async def headortail(interaction: discord.Interaction,bet: app_commands.Range[int, 1,100],choice: Choice[int] ):
    users = await getBankData()
    validUser = await isUser(str(interaction.user.id))
    if not validUser:
        users[str(interaction.user.id)] = {"balance": 0, "WalletAddress": "","TwitterAccount":""}
        with open ("bank.json","w") as f:
            json.dump(users,f)
    if bet > users[str(interaction.user.id)]["balance"]:
        await interaction.response.send_message("You don't have enough money for that bet!",ephemeral=True)
        return
        
        
    
    if validUser:
        botChoice = random.randint(0, 1)
        em = discord.Embed(title="Heads or Tails",color=discord.Color.yellow())
        em.add_field(name=f":coin: : {HelperDec[botChoice]}",value="",inline=False)
        
        if botChoice == choice.value:
            em.add_field(name="",value=f"You guessed correct! You won {bet*2} coinz",inline=False)
            await addMoney(str(interaction.user.id),bet)
        else:
            em.add_field(name="",value=f"You didn't guess correct :( You lost {bet} coinz",inline=False)
            await removeMoney(str(interaction.user.id),bet)
        await interaction.response.send_message(embed=em)
    else:
        await interaction.response.send_message(content="Please create an account first by using `/joindoonz` command.",ephemeral=True)
        
        
@headortail.error
async def on_test_error(interaction: discord.Interaction,error: app_commands.AppCommandError):
   if isinstance(error, app_commands.CommandOnCooldown):
     RemainingHours,RemainingMin,RemainingSec = await convert_seconds(error.retry_after)
     await interaction.response.send_message("Please wait for {} hours, {} minutes, {} seconds.".format(
       int(RemainingHours),int(RemainingMin),int(RemainingSec)),ephemeral=True)           
            

        
@client.tree.command(name="reload", description="Reloads the bot")
@commands.check(owner)
async def reload(interaction: discord.Interaction): 
    await client.reload_extension(f"cogs.cog1")
    embed = discord.Embed(title='Reload', description='successfully reloaded', color=0xff00c8)
    await interaction.response.send_message(embed=embed)
                
@client.tree.command(name="dailycoinz", description="Collect daily coinz")
@commands.check(holder)
@app_commands.checks.cooldown(1, 24*60*60, key=lambda i: (i.user.id))
async def dailycoinz(interaction: discord.Interaction):
    users = await getBankData()
    validUser = await isUser(str(interaction.user.id))

    for role in RoleMappedToReward:
        DesiredRole = interaction.guild.get_role(role)
        if DesiredRole in interaction.user.roles:
            if not validUser:
                users = await getBankData()
                users[str(interaction.user.id)] = {"balance": 0, "WalletAddress": "","TwitterAccount":""}
                with open ("bank.json","w") as f:
                    json.dump(users,f)
            await addMoney(str(interaction.user.id),RoleMappedToReward[role])
            em = discord.Embed(title="Daily Doonz Coins",color=discord.Color.yellow())
            em.add_field(name="",value=f"You claimed your daily {RoleMappedToReward[role]} Doonz Coinz for your <@&{role}> role.",inline=False)
            em.add_field(name="",value="Come back tommorow for more coinz or be active in the community or lucky in giveaways.:moneybag:",inline=False)
            await interaction.response.send_message(embed=em)
            return
    
        
@dailycoinz.error
async def on_test_error(interaction: discord.Interaction,error: app_commands.AppCommandError):
   if isinstance(error, app_commands.CommandOnCooldown):
     RemainingHours,RemainingMin,RemainingSec = await convert_seconds(error.retry_after)
     await interaction.response.send_message("Please wait for {} hours, {} minutes, {} seconds.".format(
       int(RemainingHours),int(RemainingMin),int(RemainingSec)),ephemeral=True)   

    

client.run(os.getenv('TOKEN'))

