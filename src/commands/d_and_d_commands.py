from discord.ext import commands
import discord
from datetime import datetime
import pytz
from models.player import Player

class DAndDCommands(commands.Cog):
    def __init__(self, bot, rs_api, d_and_d_tracker, player_data_manager):
        self.bot = bot
        self.rs_api = rs_api
        self.d_and_d_tracker = d_and_d_tracker
        self.player_data_manager = player_data_manager

    async def send_activities(self, ctx, interval: str):
        user_id = str(ctx.author.id)
        username = self.player_data_manager.get_player_name(user_id)
        
        if not username:
            await ctx.send("Please set your RuneScape name first using !setrsn <name>")
            return
        
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
            if self.d_and_d_tracker.is_available(activity.name, user_id):
                status = "🔵 Available"
            else:
                completion_time = self.d_and_d_tracker.get_completion_time(activity.name, user_id)
                next_reset = self.d_and_d_tracker._get_next_reset(completion_time, activity.name)
                status = f"🔴 Completed (Resets <t:{int(next_reset.timestamp())}:R>)"
                
            embed.add_field(
                name=activity.name,
                value=status,
                inline=False
            )
        
        await ctx.send(embed=embed)

    async def _handle_activity_with_suggestions(self, ctx, activity_name: str, action='complete'):
        matches = self.d_and_d_tracker.find_closest_activity(activity_name, 0.5)

        if len(matches) == 1:
            # If only one match, use it automatically
            matched_activity = matches[0]
            if action == 'complete':
                return await self.mark_complete(ctx, activity_name=matched_activity)
            else:
                return await self.unmark_complete(ctx, activity_name=matched_activity)
        elif matches:
            suggestion_text = "\nDid you mean one of these?\n" + "\n".join(matches)
            await ctx.send(f"Activity '{activity_name}' not found.{suggestion_text}")
        else:
            await ctx.send(f"Activity '{activity_name}' not found.")

    @commands.command(name='daily')
    async def show_daily(self, ctx):
        await self.send_activities(ctx, 'daily')

    @commands.command(name='weekly')
    async def show_weekly(self, ctx):
        await self.send_activities(ctx, 'weekly')

    @commands.command(name='monthly')
    async def show_monthly(self, ctx):
        await self.send_activities(ctx, 'monthly')

    @commands.command(name='alldnd')
    async def show_all_dnds(self, ctx):
        await self.send_activities(ctx, 'daily')
        await self.send_activities(ctx, 'weekly')
        await self.send_activities(ctx, 'monthly')

    @commands.command(name='complete')
    async def mark_complete(self, ctx, *, activity_name: str):
        user_id = str(ctx.author.id)
        activity_name = activity_name.lower().replace(' ', '_')
        
        for period in ['daily', 'weekly', 'monthly']:
            activities = getattr(self.d_and_d_tracker, f'{period}_activities')
            if activity_name in activities:
                activity = activities[activity_name]
                activity.mark_completed(user_id, self.d_and_d_tracker)
                
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
                
        await self._handle_activity_with_suggestions(ctx, activity_name, 'complete')

    @commands.command(name='uncomplete')
    async def unmark_complete(self, ctx, *, activity_name: str):
        user_id = str(ctx.author.id)
        activity_name = activity_name.lower().replace(' ', '_')
        
        for period in ['daily', 'weekly', 'monthly']:
            activities = getattr(self.d_and_d_tracker, f'{period}_activities')
            if activity_name in activities:
                if self.d_and_d_tracker.remove_completion(activity_name, user_id):
                    embed = discord.Embed(
                        title="Activity Uncompleted",
                        description=f"Removed completion status for {activities[activity_name].name}",
                        color=discord.Color.blue()
                    )
                    await ctx.send(embed=embed)
                    return
                else:
                    await ctx.send(f"Activity '{activity_name.replace('_', ' ')}' was not marked as completed.")
                return
                
        await self._handle_activity_with_suggestions(ctx, activity_name, 'uncomplete')

async def setup(bot):
    await bot.add_cog(DAndDCommands(bot))