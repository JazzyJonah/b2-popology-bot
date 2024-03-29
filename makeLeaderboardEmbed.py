from requests import get
from discord import Embed, Interaction, ButtonStyle, SelectOption
from discord.ui import View, Button, Select
from math import ceil
from threading import Thread

from makePlayerEmbeds import createPlayerEmbed, findPlayer

def createLeaderboardEmbed(page, season, result):
    apiPage = (page-1)//5+1
    endpoint = f"https://data.ninjakiwi.com/battles2/homs/season_{season-1}/leaderboard?page={apiPage}"
    allPlayers = get(endpoint).json()['body']
    start = (page-1) % 5*10
    lenPage = min([10, len(allPlayers)-start])
    
    interestingPlayers = get_interesting_players(page, season)

    em = Embed(title=f"Showing players {start+1+50*(apiPage-1)}-{start+lenPage+50*(apiPage-1)}",
               url = endpoint+"&pretty=true",
               color=int("FFFF00", 16))
    
    ranks = ""
    for i in range(1, 1+lenPage):
        ranks += str((page-1)*10+i)+"\n"
    ranks = ranks[:-1]  # removes last newline
    em.add_field(name="Rank", value=ranks, inline=True)

    displayNames = ""
    for i in range(lenPage):
        try:
            displayNames += interestingPlayers[i]['displayName']+"\n"
        except:
            print("interesting players", interestingPlayers)
            print("page", page)
            print("endpoint", endpoint)
    displayNames = displayNames[:-1]
    em.add_field(name="Username", value=displayNames, inline=True)

    scores = ""
    for i in range(lenPage):
        scores += str(interestingPlayers[i]['score'])+"\n"
    scores = scores[:-1]
    em.add_field(name="Score", value=scores, inline=True)

    result[0] = em

def get_interesting_players(page, season):
    apiPage = (page-1)//5+1
    endpoint = f"https://data.ninjakiwi.com/battles2/homs/season_{season-1}/leaderboard?page={apiPage}"
    allPlayers = get(endpoint).json()['body']

    start = (page-1) % 5*10
    lenPage = min([10, len(allPlayers)-start])
    interestingPlayers = allPlayers[start:start+lenPage]
    return interestingPlayers


class LeaderboardView(View):
    def __init__(self, page, totalPlayers, interaction, season):
        super().__init__(timeout=None)
        self.page = page
        self.totalPlayers = totalPlayers
        self.interaction = interaction
        self.season = season
        self.value = None

        if self.page > 1:
            button = LeaderboardButton(-1, self.page, self.totalPlayers, interaction, season)
            try:
                self.add_item(button)
            except:
                pass
        if self.page < ceil(self.totalPlayers/10):
            button = LeaderboardButton(1, self.page, self.totalPlayers, interaction, season)
            try:
                self.add_item(button)
            except:
                pass
        self.add_item(LeaderboardSelect(page, totalPlayers, interaction, season))
    async def interaction_check(self, interaction: Interaction):
        if interaction.user.id == self.interaction.user.id:
            return True
        else:
            await interaction.response.send_message("You do not have permission to use this.", ephemeral=True)
            return False
        
class LeaderboardButton(Button):
    def __init__(self, value, page, totalPlayers, interaction, season):
        super().__init__(style=ButtonStyle.primary, emoji = "⬅️" if value < 0 else "➡️")
        self.value = value
        self.page = page
        self.totalPlayers = totalPlayers
        self.interaction = interaction
        self.season = season
    async def callback(self, interaction: Interaction):
        # try:
            self.page += self.value
            result = [None,]
            backgroundEmbed = Thread(target=createLeaderboardEmbed, args=(self.page, self.season, result))
            backgroundEmbed.start()
            while backgroundEmbed.is_alive():
                pass
            em = result[0]
            view = LeaderboardView(page=self.page, totalPlayers=self.totalPlayers, interaction=self.interaction, season=self.season)
            await self.interaction.edit_original_response(embed=em, view=view)
            await interaction.response.defer()
        # except:
            # await interaction.followup.send("Something went wrong")

class LeaderboardSelect(Select):
    def __init__(self, page, totalPlayers, interaction, season):
        self.interestingPlayers = get_interesting_players(page, season)
        super().__init__(
            placeholder="Select a player", 
            options=[
                SelectOption(
                    label = f"{10*(page-1)+i+1}. {self.interestingPlayers[i]['displayName']}", 
                    value = i
                ) for i in range(len(self.interestingPlayers))
            ]
        )
        self.page = page
        self.totalPlayers = totalPlayers
        self.interaction = interaction
        self.season = season
        self.value = None
    async def callback(self, interaction: Interaction):
        self.value = int(interaction.data["values"][0])
        profile, ranks = findPlayer(self.season, username=self.interestingPlayers[self.value]['displayName'])
        em = createPlayerEmbed(profile, ranks, interaction, result=[None,])
        await self.interaction.edit_original_response(embed=em)
        await interaction.response.defer()
