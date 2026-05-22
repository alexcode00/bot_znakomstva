from aiogram import Bot, Dispatcher
import asyncio
import logging
from handlers import routers
import os
from dotenv import load_dotenv
from database import db
load_dotenv()
import sys


if sys.platform == "win32":
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

async def main():
    bot = Bot(token=os.getenv("BOT_TOKEN"))
    dp = Dispatcher()
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    for router in routers:
        dp.include_router(router)
    await db.connect()
    await dp.start_polling(bot)

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("exit")
