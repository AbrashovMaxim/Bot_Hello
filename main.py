from aiogram import Bot
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.dispatcher.dispatcher import Dispatcher
import asyncio

from libs.other import router
from libs.config import config

bot = Bot(token=config.get_token(), parse_mode="HTML")
dp = Dispatcher(storage=MemoryStorage())
dp.include_routers(router)

async def main():
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)

if __name__ == '__main__':

    loop = asyncio.get_event_loop()
    try:
        loop.create_task(main(), name="Main loop")
        loop.run_forever()
    finally:
        print("STOP")