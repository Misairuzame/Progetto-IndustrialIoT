import asyncio
import time
from datetime import datetime, timedelta

from print_color import print as color_print


def print(*args):
    color_print(f"\n{time.time()}\t{__name__}\t", *args, color="white", format="bold")


class TimeManager:
    def __init__(self, start: datetime, step: timedelta, speed: float = 5.0):
        """
        Costruisce il TimeManager, che controlla lo scorrere del tempo nella simulazione.

        Args:
            start: Oggetto datetime che rappresenta data e ora di partenza della simulazione.
            step: Oggetto timedelta che rappresenta di quanto avanzare la simulazione ad ogni tick.
            speed: float, rappresenta quanto tempo *reale* aspettare fra un tick e il successivo.
        """
        self.current = start

        if not timedelta(hours=1) <= step <= timedelta(hours=24):
            raise ValueError(
                f"TimeManager - step value cannot be lower than 1 hour or higher than 24! Got: {step=}"
            )
        self.step = step

        if speed < 5.0:
            raise ValueError(
                f"TimeManager - speed value cannot be lower than 5 seconds! Got: {speed=}"
            )
        self.speed = speed
        self.subscribers = []

    def subscribe(self, module):
        self.subscribers.append(module)

    async def tick(self):
        await asyncio.gather(
            *(s.update(current_time=self.current) for s in self.subscribers)
        )
        self.current += self.step

    async def run(self, steps=None):
        i = 0
        while not steps or i < steps:
            print(f"[TICK] Simulated time: {self.current}")
            await self.tick()
            time.sleep(self.speed)
            i += 1
