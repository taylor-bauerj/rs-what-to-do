import random
from models.player import Player

class ActivitySuggester:
    def __init__(self, wiki_scraper, rs_api):
        self.wiki_scraper = wiki_scraper
        self.rs_api = rs_api

    async def get_suggestions(self, player_data):
        player = Player(player_data)
        suggestions = []
        
        suggestions.extend(self._get_combat_suggestions(player))
        suggestions.extend(self._get_skill_suggestions(player))
        
        money_methods = await self.wiki_scraper.get_money_making_methods()
        if money_methods:
            suitable_methods = self._filter_methods_by_requirements(money_methods, player)
            if suitable_methods:
                suggestions.append(f"Money making suggestion: {suitable_methods[0]['name']}")
        
        return suggestions

    def _get_combat_suggestions(self, player):
        suggestions = []
        if player.combat_level >= 70:
            suggestions.append('Try God Wars Dungeon 1')
        if player.combat_level >= 80:
            suggestions.append('Challenge Elite Dungeons')
        return suggestions

    def _get_skill_suggestions(self, player):
        suggestions = []
        # Add skill-based suggestions
        return suggestions
    
    def _filter_methods_by_requirements(self, methods, player):
        suitable_methods = []
        
        for method in methods:
            requirements = method['requirements'].lower()
            can_do = True
            
            # Check if player meets level requirements
            for skill_name, skill_data in player.skills.items():
                skill_name = self.rs_api.skill_map[skill_name].lower()
                if skill_name in requirements:
                    # Extract level requirement using regex or simple parsing
                    # For now, we'll just add all methods
                    pass
                    
            if can_do:
                suitable_methods.append(method)
                
        return suitable_methods

