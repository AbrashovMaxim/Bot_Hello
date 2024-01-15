import yaml
import re

from typing import Union

class Config:
    def __init__(self) -> None:
        try:
            with open("config.yaml", "r") as f:
                self.data = yaml.safe_load(f)
                print("[CONFIG] Configuration file loaded - successfully!")
        except:
            self.data = {
                "DATABASE": {
                    "database": "nameDB",
                    "host": "localhost",
                    "port": 3306,
                    "user": "root",
                    "password": "root"
                },
                "BOTConfig": {
                    "TOKEN": "TOKEN_BOT",
                    "BOTChannel": "ID_COMMON_CHANNEL_BOT",
                    "URLChannel": "https://t.me/URL_CHANNEL_BOT/"
                },
                "BOTsConnection": {
                    0: {
                        "URLChannel": "https://t.me/URL_CHANNEL_BOT/",
                        "IDChannel": "ID_CHANNEL_BOT",
                        "DATABASE": {
                            "database": "nameDB",
                            "host": "localhost",
                            "port": 3306,
                            "user": "root",
                            "password": "root"
                        }
                    }
                }
            }
            with open("config.yaml", "w") as f:
                yaml.dump(self.data, f, default_flow_style=False)
            print("[CONFIG] Change configuration file - config.yaml!")
            exit(1)
        self.check_config()
    
    def check_config(self) -> None:
        try:
            if not(re.search("^(?:[0-9]{1,3}\\.){3}[0-9]{1,3}$", self.data["DATABASE"]["host"])):
                print("[CONFIG] Check HOST in DATABASE!")
                exit(1)
            
            if not(check_int(self.data["DATABASE"]["port"])):
                print(f"[CONFIG] Check PORT in DATABASE!")
                exit(1)
                
            if not(re.search("^[0-9]*:[a-zA-Z0-9_-]*$", self.data["BOTConfig"]["TOKEN"])):
                print(f"[CONFIG] Check TOKEN in BOTConfig")
                exit(1)

            for i in self.data["BOTsConnection"]:
                if not(re.search("^(?:[0-9]{1,3}\\.){3}[0-9]{1,3}$", self.data["BOTsConnection"][i]["DATABASE"]["host"])):
                    print(f"[CONFIG] Check HOST in BOTsConnection.{i}.DATABASE!")
                    exit(1)
            
                if not(check_int(self.data["BOTsConnection"][i]["DATABASE"]["port"])):
                    print(f"[CONFIG] Check PORT in BOTsConnection.{i}.DATABASE!")
                    exit(1)
                    
                if not(check_int(self.data["BOTsConnection"][i]["IDChannel"])):
                    print(f"[CONFIG] Check IDChannel in BOTsConnection.{i}.IDChannel")
                    exit(1)
        except Exception as e:
                print(f"[CONFIG] Problems in configuration file!\n{e}")
                exit(1)
    
    def get_token(self) -> str:
        return self.data["BOTConfig"]["TOKEN"]
    
    def get_channel(self) -> int:
        return self.data["BOTConfig"]["BOTChannel"]
    
    def get_url(self) -> str:
        return self.data["BOTConfig"]["URLChannel"]
    
    def get_channels(self) -> dict:
        channels = {}
        from libs.db import DataBase
        for i in self.data["BOTsConnection"]:
            channels[self.data["BOTsConnection"][i]["IDChannel"]] = {
                "DB": DataBase(self.data["BOTsConnection"][i]["DATABASE"]),
                "Url": self.data["BOTsConnection"][i]["URLChannel"]
            }
        return channels
    
    def get_database(self) -> dict:
        return self.data["DATABASE"]
    
def check_int(value: Union[str, int]) -> bool:
    try: 
        _temp = int(value)
        return True
    except:
        return False

config = Config()