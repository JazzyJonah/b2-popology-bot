from discord import Embed, Interaction, ButtonStyle, SelectOption
from discord.ui import View, Select, Button
from datetime import datetime

def createSimpleMatchEmbed(matches, interaction):
    totalWins = 0
    totalLosses = 0
    playerNames = ""
    otherNames = ""
    results = ""
    for match in matches:
        playerSide = "Left" if match["playerLeft"]["currentUser"] else "Right"
        otherSide = "Left" if not match["playerLeft"]["currentUser"] else "Right"
        if match["player"+playerSide]["result"] == "win":
            totalWins += 1
        elif match["player"+playerSide]["result"] == "lose":
            totalLosses += 1
        playerNames += match["player"+playerSide]["displayName"]+"\n"
        otherNames += match["player"+otherSide]["displayName"]+"\n"
        results += match["player"+playerSide]["result"]+"\n"

    em = Embed(title="Matches", 
        url=matches[-1]["player"+playerSide]["profileURL"]+"/matches?pretty=true",
        color=int('%02x%02x%02x' % (totalLosses*10, totalWins*10, 0), 16),
        timestamp=datetime.now()
    )
    em.add_field(name="Left", value=playerNames, inline=True)
    em.add_field(name="Right", value=otherNames, inline=True)
    em.add_field(name="Result", value=results, inline=True)
    em.set_footer(text=f"Total wins: {totalWins}, total losses: {totalLosses}",
        icon_url=interaction.guild.icon.url if interaction.guild.icon else interaction.user.avatar.url if interaction.user.avatar else None
    )
    
    return em
    

def createDetailedMatchEmbed(match, interaction):
    playerSide = "Left" if match["playerLeft"]["currentUser"] else "Right"
    otherSide = "Left" if not match["playerLeft"]["currentUser"] else "Right"
    em = Embed(title=f'{match["player"+playerSide]["displayName"]} vs {match["player"+otherSide]["displayName"]}', 
        url=match["player"+playerSide]["profileURL"]+"/matches?pretty=true",
        color=int('%02x%02x%02x' % (
            (0, 255, 0) if match["player"+playerSide]["result"] == "win"
            else (255, 0, 0) if match["player"+playerSide]["result"] == "lose"
            else (0, 0, 255)
        ), 16),
        timestamp=datetime.now()
    )
    playerStuff = match["player"+playerSide]
    otherStuff = match["player"+otherSide]
    em.add_field(name="Result", value=playerStuff["result"], inline=False)
    em.add_field(name="Left hero", value=playerStuff["hero"], inline=False)
    em.add_field(name="Right hero", value=otherStuff["hero"], inline=True)
    em.add_field(name="Left towers", value=f'{playerStuff["towerone"]}, {playerStuff["towertwo"]}, {playerStuff["towerthree"]}', inline=False)
    em.add_field(name="Right towers", value=f'{otherStuff["towerone"]}, {otherStuff["towertwo"]}, {otherStuff["towerthree"]}', inline=True)
    em.add_field(name="Game Type", value=match["gametype"], inline=False)
    em.add_field(name="Map", value=match["map"], inline=True)
    em.add_field(name="Rounds", value=match["endRound"], inline=True)
    em.add_field(name="Duration", value=match["duration"], inline=True)
    em.set_thumbnail(url=match["mapURL"])
    em.set_footer(text="Data is pulled from the official Ninja Kiwi API, updated about every 5 minutes.",
        icon_url=interaction.guild.icon.url if interaction.guild.icon else interaction.user.avatar.url if interaction.user.avatar else None
    )
    
    return em

class MatchView(View):
    def __init__(self, matches, interaction):
        super().__init__(timeout=None)
        self.matches = matches
        self.interaction = interaction
        self.value = None
        self.add_item(MatchSelect(matches))
    async def interaction_check(self, interaction: Interaction) -> bool:
        return interaction.user.id == self.interaction.user.id
class MatchSelect(Select):
    def __init__(self, matches):
        # playerSide = "Left" if matches[0]["playerLeft"]["currentUser"] else "Right"
        # otherSide = "Left" if not matches[0]["playerLeft"]["currentUser"] else "Right"
        super().__init__(
            placeholder="Select a match", 
            options=[
                SelectOption(
                    label = f'{i+1}. {matches[i]["playerLeft"]["displayName"]} vs {matches[i]["playerRight"]["displayName"]}', 
                    value = i
                ) for i in range(len(matches))
            ]
        )
        self.matches = matches
        self.value = None
    async def callback(self, interaction: Interaction):
        self.value = int(interaction.data["values"][0])
        em = createDetailedMatchEmbed(self.matches[self.value], interaction)
        view = BackView(self.matches, interaction)
        await interaction.response.edit_message(embed=em, view=view)

class BackView(View):
    def __init__(self, matches, interaction):
        super().__init__(timeout=None)
        self.matches = matches
        self.interaction = interaction
        self.value = None
        self.add_item(BackButton(matches))
    async def interaction_check(self, interaction: Interaction):
        return interaction.user.id == self.interaction.user.id
class BackButton(Button):
    def __init__(self, matches):
        super().__init__(style=ButtonStyle.gray, label="Back")
        self.matches = matches
        self.value = None
    async def callback(self, interaction: Interaction):
        await interaction.response.defer()
        em = createSimpleMatchEmbed(self.matches, interaction)
        view = MatchView(self.matches, interaction)
        await interaction.edit_original_response(embed=em, view=view)