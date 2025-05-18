from dataclasses import dataclass


@dataclass
class Fixpoint:
    index: int
    value: float


class Fixpoints:
    def __init__(self):
        self.points: list[Fixpoint] = []

    def add(self, location: float, value: float):
        i = int(location)
        self._add(i, value)
        if i != location:
            self._add(i + 1, value)

    def inflate(self):
        points: list[Fixpoint] = []
        prev = Fixpoint(0, 0.0)
        for fp in self.points:
            if fp.value == prev.value:
                for i in range()
        self.points = points

    def _add(self, index: int, value: float):
        self.points.append(Fixpoint(index, value))
        self.points.sort(key=lambda fp: fp.index)
