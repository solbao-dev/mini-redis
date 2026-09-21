"""최소 힙 단위 테스트."""

import unittest

from min_heap import MinHeap


class MinHeapTests(unittest.TestCase):
    def test_push_peek_pop_in_minimum_order(self):
        heap = MinHeap(initial_capacity=2)
        heap.push((5, "e"))
        heap.push((2, "b"))
        heap.push((8, "h"))
        heap.push((1, "a"))

        self.assertEqual(heap.capacity, 4)
        self.assertEqual(heap.peek(), (1, "a"))
        self.assertEqual(heap.pop(), (1, "a"))
        self.assertEqual(heap.pop(), (2, "b"))
        self.assertEqual(heap.pop(), (5, "e"))
        self.assertEqual(heap.pop(), (8, "h"))
        self.assertIsNone(heap.pop())
        self.assertEqual(heap.size(), 0)


if __name__ == "__main__":
    unittest.main()
