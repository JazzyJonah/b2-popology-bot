from requests import get
from discord import Embed
from datetime import datetime

async def checkSteamUpdates(client):
    r = get("https://api.steamcmd.net/v1/info/1276390").json()
    latestTimeUpdated = r['data']['1276390']['depots']['branches']['public']['timeupdated']
    with open('btdb2SteamReleaseTimestamp.txt', 'r+') as f:
        data = f.readlines()
        if str(latestTimeUpdated)+'\n' not in data:
            data = [str(latestTimeUpdated)+'\n']
            f.writelines(data)
            await client.get_channel(1099139880937857064).send('**BTD Battles 2** has been updated!')

async def checkSteamNews(client):
    r = get("https://api.steampowered.com/ISteamNews/GetNewsForApp/v2/?appid=1276390").json()
    latestId = r['appnews']['newsitems'][0]['gid']
    with open("btdb2SteamGid.txt", "r+") as f:
        data = f.readlines()
        if str(latestId)+'\n' not in data:
            data = [latestId+'\n']
            f.writelines(data)
            description = r['appnews']['newsitems'][0]['contents']
            description = description.replace(
                '[h1]','## ').replace('[/h1]','').replace('[list]','').replace('[/list]','').replace('[/*]','').replace('- ', '- - ').replace('[*]','- '
            )
            if('[img]' in description and '[/img]' in description):
                imgUrl = description.split('[img]')[1].split('[/img]')[0].replace('http://', 'https://')
                description = description.split('[/img]')[1]
            else:
                imgUrl = None
            descriptions = splitSmaller(description, 2048)
            embeds = []
            for i in range(len(descriptions)):
                em = Embed(
                    title = r['appnews']['newsitems'][0]['title'] + (f" ({i+1}/{len(descriptions)})" if len(descriptions) > 1 else ""),
                    description = descriptions[i],
                    url = r['appnews']['newsitems'][0]['url'],
                    color = int("00CC66", 16),
                    timestamp=datetime.fromtimestamp(r['appnews']['newsitems'][0]['date'])
                )
                if imgUrl and i == len(descriptions)-1:
                    em.set_image(url=imgUrl)
                embeds.append(em)
            for em in embeds:
                await client.get_channel(1099139880937857064).send(embed = em)

def splitSmaller(string, size):
    """Return a list of strings that are smaller than size and end with \n"""
    substrings = [substring for substring in string.split('\n') if len(substring) < size]
    returner = []
    currString = ""
    for substring in substrings:
        if len(currString) + len(substring) < size:
            currString += substring + '\n'
        else:
            returner.append(currString)
            currString = substring + '\n'
    returner.append(currString)
    return returner