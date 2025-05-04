import time
from datetime import datetime, timedelta


class TimeManager:
    def __init__(self, start: datetime, dt: timedelta, speed: float = 5.0):
        """
        Costruisce il TimeManager, che controlla la simulazione.

        Args:
            start: Oggetto datetime che rappresenta data e ora di partenza della simulazione.
            dt: Oggetto timedelta che rappresenta di quanto avanzare la simulazione ad ogni tick.
            speed: float, rappresenta quanto tempo *reale* aspettare fra un tick e il successivo.
        """
        self.current = start
        self.dt = dt
        self.speed = speed
        self.subscribers = []

    def subscribe(self, module):
        self.subscribers.append(module)

    def tick(self):
        for s in self.subscribers:
            s.update(self.current)
        self.current += self.dt

    def run(self, steps=None):
        i = 0
        while steps is None or i < steps:
            print(f"\n[TICK] Simulated time: {self.current}")
            self.tick()
            time.sleep(self.speed)
            i += 1
