"""A small doubly linked list used by the hash map and LRU tracker."""


class Node:
    """One node with previous/next links and a payload."""

    def __init__(self, data):
        self.prev = None
        self.next = None
        self.data = data


class DoublyLinkedList:
    """Doubly linked list with O(1) end and known-node operations."""

    def __init__(self):
        self.head = None
        self.tail = None
        self.length = 0

    def insert_front(self, data):
        node = Node(data)
        if self.head is None:
            self.head = self.tail = node
        else:
            node.next = self.head
            self.head.prev = node
            self.head = node
        self.length += 1
        return node

    def insert_back(self, data):
        node = Node(data)
        if self.tail is None:
            self.head = self.tail = node
        else:
            node.prev = self.tail
            self.tail.next = node
            self.tail = node
        self.length += 1
        return node

    def remove_front(self):
        if self.head is None:
            return None
        node = self.head
        self.remove_node(node)
        return node.data

    def remove_back(self):
        if self.tail is None:
            return None
        node = self.tail
        self.remove_node(node)
        return node.data

    def remove_node(self, node):
        if node is None or self.length == 0:
            return None

        if node.prev is None:
            self.head = node.next
        else:
            node.prev.next = node.next

        if node.next is None:
            self.tail = node.prev
        else:
            node.next.prev = node.prev

        node.prev = None
        node.next = None
        self.length -= 1

        if self.length == 0:
            self.head = self.tail = None
        return node.data

    def move_to_front(self, node):
        if node is None or node is self.head:
            return node

        # Detach the existing node, preserving its identity for maps that
        # store a key -> node reference (such as the LRU tracker).
        if node.prev is not None:
            node.prev.next = node.next
        if node.next is not None:
            node.next.prev = node.prev
        else:
            self.tail = node.prev

        node.prev = None
        node.next = self.head
        self.head.prev = node
        self.head = node
        return node

    def __iter__(self):
        current = self.head
        while current is not None:
            yield current
            current = current.next
