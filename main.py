from discord import Client, Intents, Interaction, Activity, ActivityType, app_commands
from discord.app_commands import CommandTree
from discord.ext import commands

from getToken import getToken

client = Client(intents = Intents.all())
tree = CommandTree(client)

@client.event
async def on_ready():
    await tree.sync()
    await client.change_presence(activity=Activity(type=ActivityType.playing, name='Bloons TD Battles 2'))
    print(f'Logged in as {client.user} (ID: {client.user.id})')

@tree.command(
    name = 'info',
    description = 'Get info about the bot'
)
@app_commands.describe(e = 'Ephemeral?')
async def info(interaction: Interaction, e: bool):
    await interaction.response.send_message('This is a test', ephemeral=e)#, ephemeral = ephemeral)

client.run(getToken())