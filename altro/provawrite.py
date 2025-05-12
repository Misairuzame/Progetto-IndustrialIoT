import asyncio

import aiofiles


async def main():
    async with aiofiles.open("/app/errors.log", "at") as errlog:
        await errlog.write("prova\n")


if __name__ == "__main__":
    asyncio.run(main())
