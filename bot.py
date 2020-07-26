import discord
from discord.ext import commands
from discord import Colour, Embed
from disputils import BotEmbedPaginator, BotConfirmation, BotMultipleChoice
import requests
from typing import List, Tuple, Any, Dict, Optional
import datetime
import calendar
from jikanpy import Jikan
from pytz import timezone

bot = commands.Bot(command_prefix='?')
day = 12
bot.remove_command("help")
EST = timezone('America/New_York')
today_date = datetime.datetime.now(EST)

with open("TOKEN.txt") as file:
    data = file.read()
    TOKEN = data


def get_anime_watched(username: str) -> List[Tuple[str, int]]:
    request = requests.get('https://myanimelist.net/animelist/' + username + '/load.json?status=2&offset=0')
    anime_json = request.json()
    try:
        r_l = [(anime['anime_title'], anime['score']) for anime in anime_json]
        r_l.sort(key=lambda x: x[1], reverse=True)
        return r_l
    except TypeError:
        return "No user Found"


def do_nothing() -> None:
    return


def generate_anime_embed(animes: List[Tuple[str, int]]) -> List[Any]:
    temp_list = []
    for a in range(0, len(animes), 10):
        temp_e = Embed(title="Completed Anime Rankings", color=0x00ff00)
        try:
            for b in range(a, a + 10):
                temp_e.add_field(name="#" + str(b + 1) + ": " + animes[b][0],
                                 value="Rated: " + str(animes[b][1]) + "/10", inline=False)
        except:
            do_nothing()
        temp_list.append(temp_e)

    return temp_list


def get_genre(dic: dict) -> List[str]:
    r_l = [genre['name'] for genre in dic]
    r_l.sort()
    return r_l


@bot.event
async def on_ready():
    print('Logged in as: {0.user}'.format(bot))


@bot.command(pass_context=True)
async def mal(ctx, *, username=""):
    if username == "":
        await ctx.send("Please enter a valid username. Usage: " + "?" + "mal <username>")
    else:
        h = get_anime_watched(username)
        if isinstance(h, list):
            list_of_pages = generate_anime_embed(h)
            page_cont = BotEmbedPaginator(ctx, list_of_pages)
            await page_cont.run()
        else:
            await ctx.send("Please enter a valid username. Usage: " + "?" + "mal <username>")


@bot.command(pass_context=True)
async def anniversary(ctx):
    months_so_far = 12
    if day > datetime.date.today().day:
        time_till_anniversary = datetime.datetime(today_date.year, today_date.month, day).replace(
            tzinfo=EST) - today_date
    elif day <= datetime.date.today().day:
        time_till_anniversary = datetime.datetime(today_date.year, today_date.month + 1, day).replace(tzinfo=EST) \
                                - today_date
    embed_anni = Embed(title="Anniversary 💖", color=0x33cc33)
    embed_anni.add_field(name="Days till anniversary",
                         value="Days: " + str(time_till_anniversary.days) + "\nHours: " +
                               str(time_till_anniversary.seconds // 3600) + "\nMinutes: " +
                               str((time_till_anniversary.seconds // 60) % 60), inline=False)
    if datetime.datetime.now(EST).day == day:
        months_so_far += 1
    embed_anni.add_field(name="How many months so far", value=months_so_far, inline=False)
    await ctx.send(embed=embed_anni)


@bot.command(pass_context=True)
async def airing(ctx, *, message=""):
    days = ['monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday', 'sunday', 'today']
    message = message.lower()
    if message == "" or message not in days:
        await ctx.send("Please enter a valid day. Usage: ?airing <day>")
    else:
        temp_list = []
        jikan = Jikan()
        if message == 'today':
            message = calendar.day_name[datetime.datetime.now(EST).weekday()]
            message = message.lower()
        new_dict = jikan.schedule(day=message)
        counter = 1
        for info in new_dict[message]:
            embed_weekly = Embed(title="Weekly Releases!", url="https://9anime.to/", color=Colour.gold())
            embed_weekly.add_field(name=str(counter) + ") " + info['title'], value="Score: " + str(info['score']),
                                   inline=False)
            embed_weekly.add_field(name="Genre", value="\n".join(get_genre(info['genres'])), inline=False)
            embed_weekly.add_field(name="Info", value=info['url'], inline=False)
            embed_weekly.set_footer(text="Time: " + str(today_date.strftime("%m/%d/%Y, %H:%M:%S")))
            embed_weekly.set_thumbnail(url=info['image_url'])
            counter += 1
            temp_list.append(embed_weekly)
        page_cont = BotEmbedPaginator(ctx, temp_list)
        await page_cont.run()


@bot.command(pass_context=True)
async def help(ctx):
    embed_help = Embed(title="Commands List", color=Colour.blurple())
    embed_help.add_field(name="Mal",
                         value="Usage: ?mal <username> \nThis command helps you get a certain user's completed anime "
                               "list",
                         inline=False)
    embed_help.add_field(name="Anniversary", value="Usage: ?anniversary\nThis is just a timer for my anniversary 😃",
                         inline=False)
    embed_help.add_field(name="Airing",
                         value="Usage: ?airing <day> or today\nThis command lets you see the shows airing on a given "
                               "day", inline=False)
    embed_help.add_field(name="Help", value="Usage: ?help\nBrings up the commands list", inline=False)
    embed_help.add_field(name="Anime", value="Usage: ?anime <anime name>\nGives a search results for the said anime",
                         inline=False)
    await ctx.send(embed=embed_help)


@bot.command(pass_context=True)
async def anime(ctx, *, message=" "):
    jikan = Jikan()
    if message == " ":
        await ctx.send("Please enter an anime: ?anime <anime name>")
    else:
        temp_lst = []
        new_dict = jikan.search('anime', query=message)
        counter = 1
        for info in new_dict['results']:
            embed_anime = Embed(title="Search", color=Colour.dark_red())
            embed_anime.add_field(name="Title", value=info['title'], inline=False)
            embed_anime.add_field(name="Score", value=info['score'], inline=False)
            embed_anime.add_field(name="Synopsis", value=info['synopsis'], inline=False)
            if info['airing'] is True:
                embed_anime.add_field(name="Airing Now", value="Yes", inline=False)
            else:
                embed_anime.add_field(name="Airing Now", value="No", inline=False)
            embed_anime.add_field(name="More info", value=info['url'], inline=False)
            embed_anime.set_thumbnail(url=info['image_url'])
            embed_anime.set_footer(text="Time: " + today_date.strftime("%m/%d/%Y, %H:%M:%S"))
            temp_lst.append(embed_anime)
            counter += 1
            if counter == 11:
                break
        page_cont = BotEmbedPaginator(ctx, temp_lst)
        await page_cont.run()


bot.run(TOKEN)
