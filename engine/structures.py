"""
Custom low-level Linear Data Structures implemented from scratch:
- MyStack (Pointer/Node-based LIFO stack)
- MyQueue (Ring-buffer / Array-based FIFO queue)
- MyPriorityQueue (Min/Max Binary Heap based queue)
No Python built-in queue or heapq modules used, adhering to DSA specifications.
"""
from typing import Any, Optional, List

class StackNode:
    def __init__(self, val: Any, next_node: Optional['StackNode'] = None):
        self.val = val
        self.next = next_node

class MyStack:
    """Pointer-based LIFO stack."""
    def __init__(self):
        self.top: Optional[StackNode] = None
        self._size = 0

    def push(self, val: Any):
        node = StackNode(val, self.top)
        self.top = node
        self._size += 1

    def pop(self) -> Any:
        if self.is_empty():
            raise IndexError("pop from empty stack")
        val = self.top.val
        self.top = self.top.next
        self._size -= 1
        return val

    def peek(self) -> Any:
        if self.is_empty():
            raise IndexError("peek from empty stack")
        return self.top.val

    def is_empty(self) -> bool:
        return self.top is None

    def size(self) -> int:
        return self._size

    def to_list(self) -> List[Any]:
        curr = self.top
        items = []
        while curr:
            items.append(curr.val)
            curr = curr.next
        return items


class MyQueue:
    """Ring-buffer based FIFO queue with dynamic resizing."""
    def __init__(self, capacity: int = 16):
        self.capacity = max(4, capacity)
        self.data: List[Optional[Any]] = [None] * self.capacity
        self.head = 0
        self.tail = 0
        self._count = 0

    def _resize(self, new_cap: int):
        new_data = [None] * new_cap
        for i in range(self._count):
            new_data[i] = self.data[(self.head + i) % self.capacity]
        self.data = new_data
        self.head = 0
        self.tail = self._count
        self.capacity = new_cap

    def enqueue(self, val: Any):
        if self._count == self.capacity:
            self._resize(self.capacity * 2)
        self.data[self.tail] = val
        self.tail = (self.tail + 1) % self.capacity
        self._count += 1

    def dequeue(self) -> Any:
        if self.is_empty():
            raise IndexError("dequeue from empty queue")
        val = self.data[self.head]
        self.data[self.head] = None
        self.head = (self.head + 1) % self.capacity
        self._count -= 1
        if 0 < self._count <= self.capacity // 4 and self.capacity > 16:
            self._resize(self.capacity // 2)
        return val

    def peek(self) -> Any:
        if self.is_empty():
            raise IndexError("peek from empty queue")
        return self.data[self.head]

    def is_empty(self) -> bool:
        return self._count == 0

    def size(self) -> int:
        return self._count

    def to_list(self) -> List[Any]:
        items = []
        for i in range(self._count):
            items.append(self.data[(self.head + i) % self.capacity])
        return items
