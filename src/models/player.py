class Player:
    def __init__(self, data, quests_data=None):
        self.name = data.get('name')
        self.combat_level = data.get('combatlevel')
        self.total_level = data.get('totalskill')
        self.quests_complete = data.get('questscomplete')
        self.quests_started = data.get('questsstarted')
        self.quests_not_started = data.get('questsnotstarted')
        self.skills = self._process_skills(data.get('skillvalues', []))
        self.activities = data.get('activities', [])
        self.quests = self._process_quests(quests_data or [])

    def _process_quests(self, quests_data):
        return {quest['title']: quest for quest in quests_data}

    def has_completed_quest(self, quest_name):
        quest = self.quests.get(quest_name)
        return quest and quest['status'] == 'COMPLETED'

    def _process_skills(self, skill_values):
        return {skill['id']: {'level': skill['level'], 'xp': skill['xp']} 
                for skill in skill_values}
