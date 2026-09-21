"""TTL 만료 시각을 관리하는 직접 구현 최소 힙."""


class MinHeap:
    """고정 길이 배열을 바탕으로 동작하는 이진 최소 힙.

    Python의 ``heapq``를 사용하지 않는다. 배열이 가득 차면 저장 공간만
    두 배로 늘리고, 힙 순서 복구는 _heapify_up/_heapify_down이 담당한다.
    """

    def __init__(self, initial_capacity=8):
        if initial_capacity < 1:
            raise ValueError("initial_capacity must be positive")
        self.items = [None] * initial_capacity
        self.capacity = initial_capacity
        self.count = 0

    def size(self):
        return self.count

    def peek(self):
        if self.count == 0:
            return None
        return self.items[0]

    def push(self, item):
        if self.count == self.capacity:
            self._grow()
        self.items[self.count] = item
        self._heapify_up(self.count)
        self.count += 1

    def pop(self):
        if self.count == 0:
            return None
        result = self.items[0]
        self.count -= 1
        if self.count == 0:
            self.items[0] = None
            return result

        self.items[0] = self.items[self.count]
        self.items[self.count] = None
        self._heapify_down(0)
        return result

    def _grow(self):
        """배열이 가득 찼을 때 용량을 두 배로 확장한다."""
        new_capacity = self.capacity * 2
        new_items = [None] * new_capacity
        for index in range(self.count):
            new_items[index] = self.items[index]
        self.items = new_items
        self.capacity = new_capacity

    def _heapify_up(self, index):
        while index > 0:
            parent = (index - 1) // 2
            if self.items[parent] <= self.items[index]:
                break
            self.items[parent], self.items[index] = (
                self.items[index], self.items[parent]
            )
            index = parent

    def _heapify_down(self, index):
        while True:
            left = index * 2 + 1
            right = index * 2 + 2
            smallest = index

            if left < self.count and self.items[left] < self.items[smallest]:
                smallest = left
            if right < self.count and self.items[right] < self.items[smallest]:
                smallest = right
            if smallest == index:
                break
            self.items[index], self.items[smallest] = (
                self.items[smallest], self.items[index]
            )
            index = smallest
