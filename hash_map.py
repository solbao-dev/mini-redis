"""A dictionary-free hash map using separate chaining."""

from linked_list import DoublyLinkedList


class HashEntry:
    """One key/value pair stored inside a bucket chain."""

    def __init__(self, key, value):
        self.key = key
        self.value = value


class HashMap:
    """Hash map with a hand-written hash function and chaining."""

    def __init__(self, initial_capacity=8):
        if initial_capacity < 1:
            raise ValueError("initial_capacity must be positive")
        self.capacity = initial_capacity
        self.count = 0
        # This list is only the indexed bucket table, not the key/value store.
        self.buckets = [None] * initial_capacity

    def _hash(self, key):
        if not isinstance(key, str):
            raise TypeError("keys must be strings")
        value = 0
        for char in key:
            value = value * 31 + ord(char)
        return value

    def _bucket_index(self, key):
        return self._hash(key) % self.capacity

    def put(self, key, value):
        index = self._bucket_index(key)
        bucket = self.buckets[index]
        if bucket is None:
            bucket = DoublyLinkedList()
            self.buckets[index] = bucket

        current = bucket.head
        while current is not None:
            entry = current.data
            if entry.key == key:
                entry.value = value
                return
            current = current.next

        bucket.insert_back(HashEntry(key, value))
        self.count += 1
        if self.count / self.capacity > 0.75:
            self._resize()

    def get(self, key, default=None):
        index = self._bucket_index(key)
        bucket = self.buckets[index]
        if bucket is None:
            return default
        current = bucket.head
        while current is not None:
            if current.data.key == key:
                return current.data.value
            current = current.next
        return default

    def contains(self, key):
        index = self._bucket_index(key)
        bucket = self.buckets[index]
        if bucket is None:
            return False
        current = bucket.head
        while current is not None:
            if current.data.key == key:
                return True
            current = current.next
        return False

    def remove(self, key):
        index = self._bucket_index(key)
        bucket = self.buckets[index]
        if bucket is None:
            return False
        current = bucket.head
        while current is not None:
            if current.data.key == key:
                bucket.remove_node(current)
                self.count -= 1
                if bucket.length == 0:
                    self.buckets[index] = None
                return True
            current = current.next
        return False

    def keys(self):
        result = [None] * self.count
        position = 0
        for bucket in self.buckets:
            if bucket is None:
                continue
            current = bucket.head
            while current is not None:
                result[position] = current.data.key
                position += 1
                current = current.next
        return result

    def size(self):
        return self.count

    def _resize(self):
        old_buckets = self.buckets
        self.capacity *= 2
        self.buckets = [None] * self.capacity
        old_count = self.count
        self.count = 0

        for bucket in old_buckets:
            if bucket is None:
                continue
            current = bucket.head
            while current is not None:
                next_node = current.next
                entry = current.data
                self.put(entry.key, entry.value)
                current = next_node

        if self.count != old_count:
            raise RuntimeError("hash map resize lost an entry")
