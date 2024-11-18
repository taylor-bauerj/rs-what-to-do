from models.d_and_d import TimedActivity
from pathlib import Path
import json
import pytz
from datetime import datetime, timedelta
from difflib import get_close_matches

class DAndDTracker:
    def __init__(self):
        self.base_dir = Path(__file__).resolve().parent.parent.parent
        self.data_dir = self.base_dir / 'data'
        self.completion_file = self.data_dir / 'd_and_d_completion.json'
        self.completion_data = self._load_completion_data()

        self.skill_map = {
            'attack': 0, 'defence': 1, 'strength': 2, 'constitution': 3,
            'ranged': 4, 'prayer': 5, 'magic': 6, 'cooking': 7,
            'woodcutting': 8, 'fletching': 9, 'fishing': 10,
            'firemaking': 11, 'crafting': 12, 'smithing': 13,
            'mining': 14, 'herblore': 15, 'agility': 16,
            'thieving': 17, 'slayer': 18, 'farming': 19,
            'runecrafting': 20, 'hunter': 21, 'construction': 22,
            'summoning': 23, 'dungeoneering': 24, 'divination': 25,
            'invention': 26, 'archaeology': 27, 'necromancy': 28
        }

        self.daily_activities = {
            'sinkholes': TimedActivity('Sinkholes', 'daily'),
            'guthixian_cache': TimedActivity('Guthixian Cache', 'daily'),
            'big_chinchompa': TimedActivity('Big Chinchompa', 'daily'),
            'phoenix_lair': TimedActivity('Phoenix Lair', 'daily', {'slayer': 51, 'quest': 'In Pyre Need'}),
            'nemi_forest': TimedActivity('Nemi Forest', 'daily'),
            'soul_reaper': TimedActivity('Soul Reaper', 'daily'),
            'red_sandstone': TimedActivity('Red Sandstone', 'daily', {'mining': 81}),
            'crystal_sandstone': TimedActivity('Crystal-Flecked Sandstone', 'daily', {'mining': 81, 'quest': 'Plague\'s End'}),
        }
        
        self.weekly_activities = {
            'penguin_hide_&_seek': TimedActivity('Penguin Hide & Seek', 'weekly'),
            'tears_of_guthix': TimedActivity('Tears of Guthix', 'weekly', {'quest': 'Tears of Guthix'}),
            'herby_werby': TimedActivity('Herby Werby', 'weekly'),
            'agoroth': TimedActivity('Agoroth', 'weekly', {'quest': 'A Shadow over Ashdale'}),
            'circus': TimedActivity('Circus', 'weekly'),
            'rush_of_blood': TimedActivity('Rush of Blood', 'weekly', {'slayer': 85, 'quest': 'Plague\'s End'}),
            'help_meg': TimedActivity('Help Meg', 'weekly'),
        }
        
        self.monthly_activities = {
            'troll_invasion': TimedActivity('Troll Invasion', 'monthly'),
            'giant_oyster': TimedActivity('Giant Oyster', 'monthly', {'quest': 'Beneath Cursed Tides'}),
            'god_statues': TimedActivity('God Statues', 'monthly'),
            'premier_club_vault': TimedActivity('Premier Club Vault', 'monthly', {'membership': 'premier'})
        }

    def _load_completion_data(self):
        self.data_dir.mkdir(exist_ok=True)
        if not self.completion_file.exists():
            self.completion_file.write_text('{}')
            return {}
        return json.loads(self.completion_file.read_text())
        
    def _save_completion_data(self):
        self.completion_file.write_text(json.dumps(self.completion_data, indent=4))
        
    def mark_completed(self, activity_name: str, user_id: str):
        if user_id not in self.completion_data:
            self.completion_data[user_id] = {}
        self.completion_data[user_id][activity_name] = datetime.now(pytz.UTC).isoformat()
        self._save_completion_data()
        
    def get_completion_time(self, activity_name: str, user_id: str):
        if user_id in self.completion_data and activity_name in self.completion_data[user_id]:
            completion_time = datetime.fromisoformat(self.completion_data[user_id][activity_name])
            return completion_time.replace(tzinfo=pytz.UTC)
        return None

    def get_available_activities(self, period, player, user_id):
        activities = getattr(self, f'{period}_activities')
        available = []
        
        for activity in activities.values():
            if activity.is_available(user_id) and self._meets_requirements(activity, player):
                available.append(activity)
                
        return available

    def _meets_requirements(self, activity, player):
        if not activity.requirements:
            return True
            
        for requirement_type, required_value in activity.requirements.items():
            if requirement_type == 'any':
                return True
            elif requirement_type == 'quest_points':
                if player.quests_complete < required_value:
                    return False
            elif requirement_type == 'combat':
                if player.combat_level < required_value:
                    return False
            elif requirement_type == 'quest':
                if not player.has_completed_quest(required_value):
                    return False
            elif requirement_type == 'membership':
                # Skip membership check for now as we can't verify this
                continue
            else:
                skill_id = self.skill_map.get(requirement_type.lower())
                if skill_id is not None and skill_id in player.skills:
                    if player.skills[skill_id]['level'] < required_value:
                        return False
                    
        return True

    def is_available(self, activity_name: str, user_id: str):
        completion_time = self.get_completion_time(activity_name, user_id)
        if not completion_time:
            return True
            
        now = datetime.now(pytz.UTC)
        next_reset = self._get_next_reset(completion_time, activity_name)
        return now >= next_reset
        
    def _get_next_reset(self, completion_time, activity_name):
        now = datetime.now(pytz.UTC)
        
        # Find which type of activity this is
        activity_type = None
        for period in ['daily', 'weekly', 'monthly']:
            activities = getattr(self, f'{period}_activities')
            if activity_name.lower().replace(' ', '_') in [name.lower() for name in activities.keys()]:
                activity_type = period
                break
                
        if activity_type == 'daily':
            # Next UTC midnight
            next_reset = now.replace(hour=0, minute=0, second=0, microsecond=0)
            if now >= next_reset:
                next_reset += timedelta(days=1)
                
        elif activity_type == 'weekly':
            # Next Wednesday UTC midnight
            days_until_wednesday = (2 - now.weekday()) % 7
            next_reset = now.replace(hour=0, minute=0, second=0, microsecond=0)
            if days_until_wednesday == 0 and now >= next_reset:
                days_until_wednesday = 7
            next_reset += timedelta(days=days_until_wednesday)
            
        else:  # monthly
            # First day of next month UTC midnight
            if now.month == 12:
                next_reset = now.replace(year=now.year + 1, month=1, day=1, hour=0, minute=0, second=0, microsecond=0)
            else:
                next_reset = now.replace(month=now.month + 1, day=1, hour=0, minute=0, second=0, microsecond=0)
                
        return next_reset

    def remove_completion(self, activity_name: str, user_id: str):
        if user_id in self.completion_data:
            # Find the actual key in completion data by comparing normalized strings
            for completed_activity in list(self.completion_data[user_id].keys()):
                if completed_activity.lower().replace(' ', '_') == activity_name.lower():
                    del self.completion_data[user_id][completed_activity]
                    self._save_completion_data()
                    return True
        return False

    def find_closest_activity(self, partial_name: str, threshold=0.6):
        search_term = partial_name.lower()
        matches = set()  # Using set to avoid duplicates
        
        # Get all activity names
        activity_names = []
        for period in ['daily', 'weekly', 'monthly']:
            activities = getattr(self, f'{period}_activities')
            for activity in activities.values():
                activity_names.append(activity.name)
        
        # Direct matching first
        for name in activity_names:
            if search_term == name.lower():
                matches.add(name)
            elif search_term in name.lower():
                matches.add(name)
                
        # If no direct matches, try fuzzy matching
        if not matches:
            fuzzy_matches = get_close_matches(search_term, [name.lower() for name in activity_names], n=3, cutoff=threshold)
            for match in fuzzy_matches:
                # Find the original name with proper capitalization
                original_name = next(name for name in activity_names if name.lower() == match)
                matches.add(original_name)
                
        return list(matches)[:3]  # Return top 3 matches




