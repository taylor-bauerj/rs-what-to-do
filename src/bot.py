from discord.ext import commands
import discord
from dotenv import load_dotenv
import os
from commands.d_and_d_commands import DAndDCommands
from commands.activity_commands import ActivityCommands
from services.rs_api import RuneScapeAPI
from services.wiki_scraper import WikiScraper
from services.activity_suggester import ActivitySuggester
from services.d_and_d_tracker import DAndDTracker

load_dotenv()
DISCORD_TOKEN = os.getenv('DISCORD_TOKEN')

bot = commands.Bot(command_prefix='!', intents=discord.Intents.all())

@bot.event
async def on_ready():
    print(f'{bot.user} has connected to Discord!')

@bot.event
async def setup_hook():
    rs_api = RuneScapeAPI()
    wiki_scraper = WikiScraper()
    activity_suggester = ActivitySuggester(wiki_scraper, rs_api)
    d_and_d_tracker = DAndDTracker()

    await bot.add_cog(DAndDCommands(bot, rs_api, d_and_d_tracker))
    await bot.add_cog(ActivityCommands(bot, rs_api, activity_suggester))

def main():
    bot.run(DISCORD_TOKEN)

if __name__ == "__main__":
    main()
