from discord import Client, Intents, AllowedMentions, Interaction, Activity, ActivityType, app_commands
from discord.app_commands import CommandTree
from threading import Thread
from requests import get
from time import time

from getToken import getToken
from makePlayerEmbeds import findPlayer, createPlayerEmbed
from makeLeaderboardEmbed import createLeaderboardEmbed, LeaderboardView
from secretInteractions import checkForSecrets
from starboard import checkStarboard


client = Client(intents = Intents.all(), allowed_mentions=AllowedMentions.none())
tree = CommandTree(client)

@client.event
async def on_ready():
    # await tree.sync()
    await client.change_presence(activity=Activity(type=ActivityType.playing, name='Bloons TD Battles 2'))
    print(f'Logged in as {client.user} (ID: {client.user.id})')

@client.event
async def on_message(message):
    if not message.author.bot:
        await checkForSecrets(message, client)

@client.event
async def on_raw_reaction_add(payload):
    await checkStarboard(client, payload)

@tree.command(
    name = 'info',
    description = 'Get info about the bot'
)
@app_commands.describe(ephemeral = 'Ephemeral?')
async def info(interaction: Interaction, ephemeral: bool = False):
    await interaction.response.send_message(
        """**List of Commands** \n
            `/info` - What you're seeing right now!
            `/ping` - Pong!
            `/leaderboard` - shows the current Battles 2 leaderboard
            `/user` - Shows information about a user, either by leaderboard position, username, or OakID
        """, 
        ephemeral=ephemeral)
    
@tree.command(
    name = 'ping',
    description = 'Pong!'
)
@app_commands.describe(ephemeral = 'Ephemeral?')
async def ping(interaction: Interaction, ephemeral: bool = False):
    x = time()
    await interaction.response.send_message("Pong!", ephemeral=ephemeral)
    x = time() - x
    with open("pings.txt", "r") as f:
        data = f.readlines()
        if x < float(data[0].split(" ")[0]):
            data = [f"{x} {interaction.user.id}"]
            with open("pings.txt", "w") as g:
                g.writelines(data)
            if not ephemeral:
                message = await interaction.original_response()
                await message.pin(reason="new wr")
            else:
                message = await interaction.channel.send(f"New wr! <@{interaction.user.id}> got a time of {str(x*1000)[:6]}||{str(x*1000)[6:]}||ms")
                await message.pin(reason="new wr")
    await interaction.edit_original_response(content=f"Pong! Response took {str(x*1000)[:6]}||{str(x*1000)[6:]}||ms\n\nThe current wr is <@{data[0].split(' ')[1]}> with a whopping time of {str(float(data[0].split(' ')[0])*1000)[:6]}||{str(float(data[0].split(' ')[0])*1000)[6:]}||ms")
    
@tree.command(
    name = 'leaderboard',
    description = 'Get the current leaderboard'
)
@app_commands.describe(season = 'Season', page = 'Page', ephemeral = 'Ephemeral?')
async def leaderboard(interaction: Interaction, season: int = 16, page: int = 1, ephemeral: bool = False):
    await interaction.response.defer(ephemeral=ephemeral)
    try:
        if season < 9:
            await interaction.followup.send("Season must be 9 or higher", ephemeral=ephemeral)
            return
        result = [None,]
        backgroundEmbed = Thread(target=createLeaderboardEmbed, args=(page, season, result))
        backgroundEmbed.start()
        while backgroundEmbed.is_alive():
            pass
        em = result[0]

        totalPlayers = get("https://data.ninjakiwi.com/battles2/homs/").json()["body"]
        seasonIndex = next((i for i in range(len(totalPlayers)) if totalPlayers[i]["name"][-2:] == str(season)), None)
        totalPlayers = totalPlayers[seasonIndex]["totalScores"]
        view = LeaderboardView(page=page, totalPlayers=totalPlayers, interaction=interaction, season=season)
        await interaction.followup.send(embed=em, view=view)
    except:
        await interaction.followup.send("Something went wrong")

    
userGroup = app_commands.Group(name = 'user', description='Get info about a user')
@userGroup.command(
    name = 'leaderboard_position',
    description = 'Get info about a user by leaderboard position'
)
@app_commands.describe(leaderboard_position = 'Leaderboard position', season = 'Season', ephemeral = 'Ephemeral?')
async def user_leaderboard_position(interaction: Interaction, leaderboard_position: int, season: int = 16, ephemeral: bool = False):
    await interaction.response.defer(ephemeral=ephemeral)
    try:
        leaderboard_position -= 1
        if season < 9:
            await interaction.followup.send("Season must be 9 or higher", ephemeral=ephemeral)
            return
        profile, ranks = findPlayer(season, position=leaderboard_position)

        result = [None,]
        backgroundEmbed = Thread(target=createPlayerEmbed, args=(profile, ranks, interaction, result))
        backgroundEmbed.start()
        while backgroundEmbed.is_alive():
            pass
        em = result[0]
        await interaction.followup.send(embed=em)
    except:
        await interaction.followup.send("Something went wrong")

@userGroup.command(
    name = 'username',
    description = 'Get info about a user by username'
)
@app_commands.describe(username = 'Username', season = 'Season', ephemeral = 'Ephemeral?')
async def user_username(interaction: Interaction, username: str, season: int = 16, ephemeral: bool = False):
    await interaction.response.defer(ephemeral=ephemeral)
    try:
        if season < 9:
            await interaction.response.send_message("Season must be 9 or higher", ephemeral=ephemeral)
            return
        profile, ranks = findPlayer(season, username=username)

        result = [None,]
        backgroundEmbed = Thread(target=createPlayerEmbed, args=(profile, ranks, interaction, result))
        backgroundEmbed.start()
        while backgroundEmbed.is_alive():
            pass
        em = result[0]
        await interaction.followup.send(embed=em)
    except:
        await interaction.followup.send("Something went wrong")

@userGroup.command(
    name = 'oakid',
    description = 'Get info about a user by OakID'
)
@app_commands.describe(oakid = 'OakID', season = 'Season', ephemeral = 'Ephemeral?')
async def user_oakid(interaction: Interaction, oakid: int, season: int = 16, ephemeral: bool = False):
    await interaction.response.defer(ephemeral=ephemeral)
    try:
        if season < 9:
            await interaction.response.send_message("Season must be 9 or higher", ephemeral=ephemeral)
            return
        profile, ranks = findPlayer(season, oakID=oakid)

        result = [None,]
        backgroundEmbed = Thread(target=createPlayerEmbed, args=(profile, ranks, interaction, result))
        backgroundEmbed.start()
        while backgroundEmbed.is_alive():
            pass
        em = result[0]
        await interaction.followup.send(embed=em)
    except:
        await interaction.followup.send("Something went wrong")



tree.add_command(userGroup)
client.run(getToken())