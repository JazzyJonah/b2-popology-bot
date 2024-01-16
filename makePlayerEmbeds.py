from requests import get
from discord import Embed

def findPlayer(season, username=None, oakID=None, position=None, page=1):
    if username:
        r = get(f"https://data.ninjakiwi.com/battles2/homs/season_{season-1}/leaderboard?page={page}").json()
        if player := next((x for x in r['body'] if x['displayName'].lower() == username.lower()), False):
            profile = get(player['profile']).json()['body']
            ranks = get(profile['homs']).json()['body']
            for i in range(len(ranks)):
                if ranks[i]['name'][-2:] == str(season):
                    ranks = ranks[i]
                    break
            else:
                ranks = ranks[0]
            return profile, ranks
        return findPlayer(season, username=username, page=page+1)
    
    elif oakID:
        profile = get(f"https://data.ninjakiwi.com/battles2/users/{oakID}").json()['body']
        ranks = get(f"https://data.ninjakiwi.com/battles2/users/{oakID}/homs").json()['body']
        for i in range(len(ranks)):
            if ranks[i]['name'][-2:] == str(season):
                ranks = ranks[i]
                break
        else:
            ranks = ranks[0]
        return profile, ranks
    
    elif position != None:
        page = position//50+1
        r = get(f"https://data.ninjakiwi.com/battles2/homs/season_{season-1}/leaderboard?page={page}").json()
        player = r['body'][position % 50]
        profile = get(player['profile']).json()['body']
        ranks = get(profile['homs']).json()['body']
        for i in range(len(ranks)):
            if ranks[i]['name'][-2:] == str(season):
                ranks = ranks[i]
                break
        else:
            ranks = ranks[0]
        return profile, ranks
    
def createPlayerEmbed(profile, ranks, interaction, result):
    displayName = profile['displayName']
    score = ranks['score']

    avatar = profile['equippedAvatarURL']
    wins = profile['rankedStats']['wins']
    draws = profile['rankedStats']['draws']
    losses = profile['rankedStats']['losses']
    highestWinStreak = profile['rankedStats']['highest_win_streak']
    color = int("A020F0", 16) if profile["is_vip"] or profile["is_club_member"] else None
    minUses = float('inf')
    for item in profile["_towers"]:
        if item["used"] < minUses and item["type"] not in ["Quincy", "Quincy_Cyber", "Gwendolin", "Gwendolin_Science", "Obyn", "Obyn_Ocean", "StrikerJones", "StrikerJones_Biker", "Churchill", "Churchill_Sentai", "Benjamin", "Benjamin_DJ", "Ezili", "Ezili_SmudgeCat", "PatFusty", "PatFusty_Snowman", "Adora", "Adora_JoanOfArc", "Jericho", "Jericho_Highwayman", "Jericho_StarCaptain", "BananaFarmer", "RoboBloon"]:
            minUses = item["used"]
            minTower = item["type"]

    totalPlayers = ranks['totalScores']

    em = Embed(
        title = displayName,
        url = profile['matches']+'?pretty=true',
        description = f'Showing stats for #{ranks['rank']}/{totalPlayers}: {displayName}',
        color = color
    )
    em.set_thumbnail(url=avatar)

    em.add_field(name='Score', value=score, inline=False)
    em.add_field(name='Wins', value=wins, inline=True)
    em.add_field(name='Draws', value=draws, inline=True)
    em.add_field(name="Losses", value=losses, inline=True)
    em.add_field(name="Highest Win Streak", value=highestWinStreak, inline=False)
    em.add_field(name="Least Used Tower", value=f"{minTower}: {minUses}")
    em.set_footer(text="Data is from the official Ninja Kiwi API, updated about every 5 minutes.",
                  icon_url=interaction.guild.icon.url if interaction.guild.icon else interaction.user.avatar.url)
    
    result[0] = em
    return em



