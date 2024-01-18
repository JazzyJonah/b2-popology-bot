from discord import Embed
from datetime import datetime

async def checkStarboard(client, payload):
    channel = client.get_channel(payload.channel_id)
    message = await channel.fetch_message(payload.message_id)
    emoji = payload.emoji
    if message.channel.id == 1131006164197441566 and str(emoji) == "🔼":
        listOfReactions = message.reactions
        downvotes = 0
        for r in listOfReactions:
            if str(r.emoji) == '🔽':
                downvotes = r.count
            if str(r.emoji) == "🔼":
                reaction = r
                
        if reaction.count - downvotes >= 8:
            with open("popularSuggestionsPosted.txt", "r+") as f:
                data = f.readlines()
                for line in data:
                    if str(message.id) in line:
                        messagePosted = True
                        break
                else:
                    data.append(str(message.id)+'\n')
                    f.writelines(data)
                    messagePosted = False
            f.close()
            
            if not messagePosted:
                em = Embed(
                    title = f"Suggestion by {message.author.display_name}",
                    description = message.content,
                    url = f"https://discord.com/channels/{message.guild.id}/{message.channel.id}/{message.id}",
                    timestamp = datetime.today(),
                    color = int("00CC66", 16)
                )
                em.set_footer(text = f"Suggestion by {message.author.name}", icon_url = message.guild.icon.url if message.guild.icon else None)

                message = await client.get_channel(1131006286683701340).send(embed = em)
                await message.publish()