import heapq
from types import NoneType

from typing import TypeVar

T = TypeVar('T')


class PriorityElem:
    def __init__(self, prio: float, data):
        self.prio = prio
        self.data = data

    def __eq__(self, other):
        return self.prio == other.prio

    def __lt__(self, other):
        return self.prio < other.prio


class PriorityQueue:
    def __init__(self):
        self.elements: list[PriorityElem] = []

    def empty(self) -> bool:
        return not self.elements

    def put(self, item: T, priority: float):
        heapq.heappush(self.elements, PriorityElem(priority, item))

    def get(self) -> T:
        return heapq.heappop(self.elements).data
