from datetime import datetime
from typing import Any
from sqlalchemy import create_engine, Column, String, Integer, Boolean, DateTime, insert, update, select
from sqlalchemy.orm import Session
from sqlalchemy.ext.declarative import declarative_base

from libs.config import config

Base = declarative_base()

class Users(Base):
    __tablename__ = "hb_users"

    id = Column("id", Integer, primary_key=True)
    user_id = Column("user_id", String(255))
    is_spam = Column("is_spam", Boolean, default=False)
    is_ban = Column("is_ban", Boolean, default=False)
    from_channel = Column("from_channel", String(255), default="-1")
    to_channel = Column("to_channel", String(255), default="-1")
    last_message = Column("last_message", String(255))

class Statistic(Base):
    __tablename__ = "hb_statistic"

    id = Column("id", Integer, primary_key=True)
    data = Column("data", String(10))
    users_bot = Column("users_bot", Integer, default=0) # - Которые присоединились в бот
    users_join = Column("users_join", Integer, default=0) # - Которые присоединились к каналу
    users_spam = Column("users_spam", Integer, default=0) # - Которые дали согласие на получение спама
    users_left = Column("users_left", Integer, default=0) # - Которые покинули канал
    users_block = Column("users_block", Integer, default=0) # - Которые заблокировали бота

class Requests(Base):
    __tablename__ = "hb_requests"

    id = Column("id", Integer, primary_key=True)
    user_id = Column("user_id", String(255))

class DataBase:
    def __init__(self, db: dict) -> None:
        try:
            self.db = f'mysql+pymysql://{db["user"]}:{db["password"]}@{db["host"]}:{db["port"]}/{db["database"]}';
            self.engine = create_engine(self.db, pool_pre_ping=True, pool_recycle=3600)
            print("База данных создана и успешно подключена к MySQL")
            Base.metadata.create_all(self.engine)
        except Exception as e: print("[DATABASE] Error connection:\n", e); exit(1)
        
    
    def _insert(self, obj: Base) -> None:
        with Session(self.engine) as session:
            session.add(obj)
            session.commit()

    def _select_More(self, table: Base, **where: Any) -> dict:
        with Session(self.engine) as session:
            obj = session.query(table).filter_by(**where).all()
            return obj

    def _select_One(self, table: Base, **where: Any) -> dict:
        with Session(self.engine) as session:
            obj = session.query(table).filter_by(**where).one_or_none()
            return obj
    
    def _exist(self, table: Base, **where: Any) -> bool:
        with Session(self.engine) as session:
            print(where)
            obj = session.query(table).filter_by(**where).one_or_none()
            if obj == None: return False
            else: return True

    
    def _delete(self, table: Base, **where: Any) -> bool:
        with Session(self.engine) as session:
            obj = session.query(table).filter_by(**where).one_or_none()
            if obj == None: return False
            else: 
                session.delete(obj)
                session.commit()
                return True
            
    def _update(self, table: Base, seta: dict = {}, **where: Any) -> bool:
        with Session(self.engine) as session:
            obj = session.query(table).filter_by(**where).one_or_none()
            if obj == None: return False
            else: 
                if table == Users:
                    if 'user_id' in seta: obj.user_id = str(seta['user_id'])
                    if 'is_spam' in seta: obj.is_spam = seta['is_spam']
                    if 'is_ban' in seta: obj.is_ban = seta['is_ban']
                    if 'from_channel' in seta: obj.from_channel = str(seta['from_channel'])
                    if 'to_channel' in seta: obj.to_channel = str(seta['to_channel'])
                    if 'last_message' in seta: obj.last_message = str(seta['last_message'])
                elif table == Statistic:
                    if 'data' in seta: obj.data = str(seta['data'])
                    if 'users_bot' in seta: obj.users_bot = str(seta['users_bot'])
                    if 'users_join' in seta: obj.users_join = seta['users_join']
                    if 'users_spam' in seta: obj.users_spam = seta['users_spam']
                    if 'users_left' in seta: obj.users_left = seta['users_left']
                    if 'users_block' in seta: obj.users_block = seta['users_block']
                elif table == Requests:
                    if 'user_id' in seta: obj.user_id = str(seta['user_id'])
                session.commit()
                return True

    def _plus_stat(self, name: str = "", value: int = 1) -> None:
        if self._exist(Statistic, data=datetime.now().strftime("%d-%m-%Y")):
            getData = self._select_One(Statistic, data=datetime.now().strftime("%d-%m-%Y"))
            if getData == "users_bot": value += getData.users_bot
            elif getData == "users_join": value += getData.users_join
            elif getData == "users_spam": value += getData.users_spam
            elif getData == "users_left": value += getData.users_left
            elif getData == "users_block": value += getData.users_block
            self._update(Statistic, {name: value}, data=datetime.now().strftime("%d-%m-%Y"))
        else:
            self._insert(Statistic(data=datetime.now().strftime("%d-%m-%Y")))
            self._update(Statistic, {name: value}, data=datetime.now().strftime("%d-%m-%Y"))


db = DataBase(config.get_database())