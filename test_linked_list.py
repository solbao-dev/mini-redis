"""이중 연결 리스트 단위 테스트."""

import unittest

from linked_list import DoublyLinkedList


class DoublyLinkedListTests(unittest.TestCase):
    def test_insert_front_and_back(self):
        linked = DoublyLinkedList()
        middle = linked.insert_front("B")
        linked.insert_front("A")
        linked.insert_back("C")

        self.assertEqual(linked.head.data, "A")
        self.assertEqual(linked.tail.data, "C")
        self.assertIs(linked.head.next, middle)
        self.assertIs(middle.prev, linked.head)
        self.assertEqual(linked.length, 3)

    def test_remove_front_back_and_middle(self):
        linked = DoublyLinkedList()
        linked.insert_back("A")
        middle = linked.insert_back("B")
        linked.insert_back("C")

        self.assertEqual(linked.remove_node(middle), "B")
        self.assertEqual(linked.remove_front(), "A")
        self.assertEqual(linked.remove_back(), "C")
        self.assertIsNone(linked.head)
        self.assertIsNone(linked.tail)
        self.assertEqual(linked.length, 0)

    def test_move_to_front_keeps_same_node(self):
        linked = DoublyLinkedList()
        linked.insert_back("A")
        linked.insert_back("B")
        last = linked.insert_back("C")

        moved = linked.move_to_front(last)

        self.assertIs(moved, last)
        self.assertIs(linked.head, last)
        self.assertEqual(linked.tail.data, "B")
        self.assertEqual(linked.length, 3)


if __name__ == "__main__":
    unittest.main()
