"""Configuration handling"""

import json
import os
from pathlib import Path


DEFAULT_CONFIG = {
    "default_provider": "openai",
    "default_model": None,
    "csv_path": "waitb_results.csv",
    "max_attempts": 6,
}


class Config:
    def __init__(self, config_path: str = None):
        self.config_path = config_path or self._find_config()
        self.data = self._load()
    
    def _find_config(self) -> str:
        local_config = os.path.join(os.getcwd(), "waitb_config.json")
        if os.path.exists(local_config):
            return local_config
        
        home_config = os.path.join(str(Path.home()), ".waitb", "config.json")
        if os.path.exists(home_config):
            return home_config
        
        return local_config
    
    def _load(self) -> dict:
        if os.path.exists(self.config_path):
            with open(self.config_path, "r") as f:
                data = json.load(f)
        else:
            data = DEFAULT_CONFIG.copy()
            self.save(data)
        return data
    
    def save(self, data: dict = None):
        if data is None:
            data = self.data
        os.makedirs(os.path.dirname(self.config_path) or ".", exist_ok=True)
        with open(self.config_path, "w") as f:
            json.dump(data, f, indent=2)
    
    def get(self, key: str, default=None):
        return self.data.get(key, default)
    
    def set(self, key: str, value):
        self.data[key] = value
        self.save()
