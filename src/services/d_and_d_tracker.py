from models.d_and_d import TimedActivity

class DAndDTracker:
    def __init__(self):
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
            'caches': TimedActivity('Guthixian Cache', 'daily'),
            'big_chinchompa': TimedActivity('Big Chinchompa', 'daily'),
            'phoenix': TimedActivity('Phoenix Lair', 'daily', {'slayer': 51, 'quest': 'In Pyre Need'}),
            'nemi_forest': TimedActivity('Nemi Forest', 'daily'),
            'soul_reaper': TimedActivity('Soul Reaper', 'daily'),
            'sandstone': TimedActivity('Red Sandstone', 'daily', {'mining': 81}),
            'crystal_sandstone': TimedActivity('Crystal-Flecked Sandstone', 'daily', {'mining': 81, 'quest': 'Plague\'s End'}),
        }
        
        self.weekly_activities = {
            'penguin_hide_seek': TimedActivity('Penguin Hide & Seek', 'weekly'),
            'tears_of_guthix': TimedActivity('Tears of Guthix', 'weekly', {'quest': 'Tears of Guthix'}),
            'herby_werby': TimedActivity('Herby Werby', 'weekly'),
            'agoroth': TimedActivity('Agoroth', 'weekly', {'quest': 'A Shadow over Ashdale'}),
            'circus': TimedActivity('Circus', 'weekly'),
            'rush_of_blood': TimedActivity('Rush of Blood', 'weekly', {'slayer': 85, 'quest': 'Plague\'s End'}),
            'meg': TimedActivity('Help Meg', 'weekly'),
        }
        
        self.monthly_activities = {
            'troll_invasion': TimedActivity('Troll Invasion', 'monthly'),
            'giant_oyster': TimedActivity('Giant Oyster', 'monthly', {'quest': 'Beneath Cursed Tides'}),
            'god_statues': TimedActivity('God Statues', 'monthly'),
            'premier_vault': TimedActivity('Premier Club Vault', 'monthly', {'membership': 'premier'})
        }

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

