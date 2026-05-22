import asyncio

async def cat():
    for _ in range(3):
        print("cat")
        await asyncio.sleep(2)

async def dog():
    for _ in range(3):
        print("dog")
        await asyncio.sleep(1)

async def main():
    await asyncio.gather(cat(), dog())
asyncio.run(main())