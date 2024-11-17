import requests

class RuneScapeAPI:
    def __init__(self):
        self.base_url = "https://apps.runescape.com/runemetrics"
        self.skill_map = {
            0: 'Attack', 1: 'Defence', 2: 'Strength', 3: 'Constitution', 
            4: 'Ranged', 5: 'Prayer', 6: 'Magic', 7: 'Cooking', 
            8: 'Woodcutting', 9: 'Fletching', 10: 'Fishing', 
            11: 'Firemaking', 12: 'Crafting', 13: 'Smithing', 
            14: 'Mining', 15: 'Herblore', 16: 'Agility', 
            17: 'Thieving', 18: 'Slayer', 19: 'Farming', 
            20: 'Runecrafting', 21: 'Hunter', 22: 'Construction', 
            23: 'Summoning', 24: 'Dungeoneering', 25: 'Divination',
            26: 'Invention', 27: 'Archaeology', 28: 'Necromancy'
        }

    def get_player_stats(self, username):
        url = f"{self.base_url}/profile/profile?user={username}&activities=20"
        response = requests.get(url)
        return response.json()
    
    def get_player_quests(self, username):
        url = f"{self.base_url}/quests?user={username}"
        response = requests.get(url)
        return response.json().get('quests', [])
