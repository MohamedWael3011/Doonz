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
load_dotenv()
intents = discord.Intents.all()

client = commands.Bot(command_prefix='.', intents=intents)

ShopItems = {
    "Doonz Editions NFT - Claimable Ticket -" :(4000,"Your ticket to claim a NFT from Doonz NFT Editions Collections on OpenSea"),
    "Doonz NFT Airdrop - Claimable Ticket -" :(6000,"Your ticket to clain a Doonz NFT airdrop."),
    "Doonz Raffle Ticket" :(300,"Your ticked to join special raffles here on discord. **Please not that you will be granted the role after claiming this shop item and role will be removed after the raffle ends.**"), 
}

RoleMappedToReward = {
    1136242811004518490: 500,
    1136242648127123537:250,
    1123574209059237929:150,
    1136240524555194398: 30,
    1123573342738329650:10,
    1083474077282468021:20
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
            

  

        
@client.event
async def on_ready():
    print('Doonz is running! Currently serving {0.user}'.format(client))
    await client.tree.sync()
    await dailygiveaway.start()

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

async def CreateAccount(userid,matic,twitter):
    users = await getBankData()
    users[userid] = {"balance": 0, "WalletAddress": matic,"TwitterAccount":twitter}
    with open ("bank.json","w") as f:
        json.dump(users,f)    
    


@client.tree.command(name="joindoonz", description="registering your account in Doonz's Discord eco system!")
async def joindoonz(interaction: discord.Interaction,matic_address: str,twitter_account: str):
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
    try:
        users = await getBankData()
        UserBalance = users[str(interaction.user.id)]["balance"]
        em = discord.Embed(title=f"{interaction.user.name}'s Balance",color=discord.Color.yellow())
        em.add_field(name= "",value=f"Your current balance is: {UserBalance}")
        await interaction.response.send_message(embed=em,ephemeral=True)
    except:
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
        
        
@tasks.loop(hours=24)
async def dailygiveaway():
    guild = discord.utils.get(client.guilds, id=1123569723314020452)
    channel = guild.get_channel(1139892842324566157)
    #role = discord.utils.get(guild.get_role, id=1083474077282468021)
    em = discord.Embed(title="Daily Coins Giveaway",color=discord.Color.yellow())
    endTime = datetime.datetime.now() + datetime.timedelta(hours=24)
    em.add_field(name="",value="Prize: 100 Coins",inline=False)
    DisplayedTime = endTime.timestamp()
    em.add_field(name="",value= f"Ends At: {discord.utils.format_dt(datetime.datetime.fromtimestamp(DisplayedTime), 'R')}",inline=False)
    my_msg = await channel.send(embed=em)
    await my_msg.add_reaction("🎉")
    await asyncio.sleep(24*60*60)
    new_msg = await channel.fetch_message(my_msg.id)
    users = []
    for reaction in new_msg.reactions:
        if reaction.emoji == '🎉':
            async for user in reaction.users():
                if user != client.user:
                    users.append(user)
    try:
        winner = random.choice(users)
        await channel.send(f"Congratulations {winner.mention} for winning the daily coin giveaway!")
        try:
            await addMoney(str(winner.id),100)
        except:
            users = await getBankData()
            users[str(winner.id)] = {"balance": 100, "WalletAddress": "","TwitterAccount":""}
            with open ("bank.json","w") as f:
                json.dump(users,f)
    except:
        pass
        
        
    
@client.tree.command(name="user_info", description="Displays user's info")
async def user_info(interaction: discord.Interaction,user: discord.User): 
    validuser = await isUser(str(interaction.user.id))
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
 
HelperDec = {0:"Head",
             1:"Tail"}

cooldownobj = app_commands.Cooldown(1, 604.0)

def cooldown_checker(interaction: discord.Interaction) -> Optional[app_commands.Cooldown]:
    return cooldownobj
@client.tree.command(name="headortail", description="If you win it gives you double the amount you bet, if you lose you lose your bet :( MAXIMUM BET: 100")
@app_commands.choices(
    choice =  [Choice(name="Head", value=0),Choice(name="Tail",value=0)]
)
@commands.check(owner)
@app_commands.checks.dynamic_cooldown(cooldown_checker,key=lambda i: (i.user.id))
async def headortail(interaction: discord.Interaction,bet: int,choice: Choice[int] ):
    users = await getBankData()
    if bet > 100:
        await interaction.response.send_message("Maximum you can bet is 100 coins!",ephemeral=True)
        app_commands.Cooldown.reset(cooldownobj)
        return
    validUser = await isUser(str(interaction.user.id))
    if bet > users[str(interaction.user.id)]["balance"]:
        await interaction.response.send_message("You don't have enough money for that bet!",ephemeral=True)
        app_commands.Cooldown.reset(cooldownobj)
        return
        
        
    
    if validUser:
        botChoice = random.randint(0, 1)
        em = discord.Embed(title="Head or Tail",color=discord.Color.yellow())
        em.add_field(name=f":coin: : {HelperDec[botChoice]}",value="",inline=False)
        
        if botChoice == choice.value:
            em.add_field(name="",value=f"You guessed correct! You won {bet*2} coins",inline=False)
            await addMoney(str(interaction.user.id),bet)
        else:
            em.add_field(name="",value=f"You didn't guess correct :( You lost {bet} coins",inline=False)
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
            em.add_field(name="",value=f"You claimed your daily {RoleMappedToReward[role]} Doonz Coinz for your <@&{role}> role.",inline=False)
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
