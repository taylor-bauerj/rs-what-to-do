from discord.ext import commands
import discord

class ActivityCommands(commands.Cog):
    def __init__(self, bot, rs_api, activity_suggester):
        self.bot = bot
        self.rs_api = rs_api
        self.activity_suggester = activity_suggester

    @commands.command(name='whatdo')
    async def suggest_activity(self, ctx, username: str):
        try:
            player_data = self.rs_api.get_player_stats(username)
            
            if 'error' in player_data:
                await ctx.send(f"Could not find player: {username}")
                return

            suggestions = await self.activity_suggester.get_suggestions(player_data)
            
            embed = discord.Embed(
                title=f"Suggested activities for {username}",
                color=discord.Color.blue()
            )
            
            for i, suggestion in enumerate(suggestions[:5], 1):
                embed.add_field(
                    name=f"Suggestion {i}",
                    value=suggestion,
                    inline=False
                )

            await ctx.send(embed=embed)

        except Exception as e:
            await ctx.send(f"An error occurred: {str(e)}")
