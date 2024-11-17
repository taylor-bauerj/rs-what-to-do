from discord.ext import commands
import discord
from datetime import datetime
import pytz
from models.player import Player

class DAndDCommands(commands.Cog):
    def __init__(self, bot, rs_api, d_and_d_tracker):
        self.bot = bot
        self.rs_api = rs_api
        self.d_and_d_tracker = d_and_d_tracker

    async def send_activities(self, ctx, username: str, interval: str):
        player_data = self.rs_api.get_player_stats(username)
        quests_data = self.rs_api.get_player_quests(username)
        player = Player(player_data, quests_data)
        user_id = str(ctx.author.id)

        activity_values = []
        match interval:
            case 'daily':
                activity_values = self.d_and_d_tracker.daily_activities.values()
            case 'weekly':
                activity_values = self.d_and_d_tracker.weekly_activities.values()
            case 'monthly':
                activity_values = self.d_and_d_tracker.monthly_activities.values()
            case _:
                await ctx.send("Invalid interval. Please use 'daily', 'weekly', or 'monthly'.")
                return
        
        # Get all activities that meet requirements, regardless of completion
        activities = []
        for activity in activity_values:
            if self.d_and_d_tracker._meets_requirements(activity, player):
                activities.append(activity)
        
        embed = discord.Embed(
            title=f"{interval} D&Ds available for {username}",
            color=discord.Color.green()
        )
        
        for activity in activities:
            if activity.is_available(user_id):
                status = "🔵 Available"
            else:
                next_reset = activity._get_next_reset(activity.last_completed[user_id])
                status = f"🔴 Completed (Resets <t:{int(next_reset.timestamp())}:R>)"
                
            embed.add_field(
                name=activity.name,
                value=status,
                inline=False
            )
        
        await ctx.send(embed=embed)

    @commands.command(name='daily')
    async def show_daily(self, ctx, username: str):
        await self.send_activities(ctx, username, 'daily')

    @commands.command(name='weekly')
    async def show_weekly(self, ctx, username: str):
        await self.send_activities(ctx, username, 'weekly')

    @commands.command(name='monthly')
    async def show_monthly(self, ctx, username: str):
        await self.send_activities(ctx, username, 'monthly')

    @commands.command(name='complete')
    async def mark_complete(self, ctx, activity_name: str):
        user_id = str(ctx.author.id)
        activity_name = activity_name.lower()
        
        for period in ['daily', 'weekly', 'monthly']:
            activities = getattr(self.d_and_d_tracker, f'{period}_activities')
            if activity_name in activities:
                activity = activities[activity_name]
                activity.mark_completed(user_id)
                
                embed = discord.Embed(
                    title="Activity Completed!",
                    description=f"Marked {activity.name} as completed.",
                    color=discord.Color.green()
                )
                
                next_reset = activity._get_next_reset(datetime.utcnow().replace(tzinfo=pytz.UTC))
                embed.add_field(
                    name="Next Reset",
                    value=f"<t:{int(next_reset.timestamp())}:R>",
                    inline=False
                )
                
                await ctx.send(embed=embed)
                return
                
        await ctx.send(f"Activity '{activity_name}' not found.")

async def setup(bot):
    await bot.add_cog(DAndDCommands(bot))