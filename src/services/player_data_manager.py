import json
import os
from pathlib import Path

class PlayerDataManager:
    def __init__(self):
        self.base_dir = Path(__file__).resolve().parent.parent.parent
        self.data_dir = self.base_dir / 'data'
        self.data_file = self.data_dir / 'player_data.json'
        self.player_names = self._load_data()
        
    def _load_data(self):
        self.data_dir.mkdir(exist_ok=True)
        if not self.data_file.exists():
            self.data_file.write_text('{}')
            return {}
        return json.loads(self.data_file.read_text())
        
    def _save_data(self):
        self.data_file.write_text(json.dumps(self.player_names, indent=4))

    def set_player_name(self, discord_id: str, player_name: str):
        self.player_names[discord_id] = player_name
        self._save_data()
        return True

    def get_player_name(self, discord_id: str):
        return self.player_names.get(discord_id)

async def setup(bot):
    await bot.add_cog(PlayerDataManager(bot))