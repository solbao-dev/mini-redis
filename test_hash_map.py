"""체이닝 해시맵 단위 테스트."""

import unittest

from hash_map import HashMap


class HashMapTests(unittest.TestCase):
    def test_put_get_contains_remove_and_size(self):
        table = HashMap(initial_capacity=8)
        table.put("name", "Alice")
        table.put("city", "Seoul")

        self.assertEqual(table.get("name"), "Alice")
        self.assertTrue(table.contains("city"))
        self.assertEqual(table.size(), 2)
        self.assertTrue(table.remove("name"))
        self.assertFalse(table.contains("name"))
        self.assertEqual(table.size(), 1)

    def test_existing_key_updates_without_growing_size(self):
        table = HashMap()
        table.put("name", "Alice")
        table.put("name", "Bob")
        self.assertEqual(table.get("name"), "Bob")
        self.assertEqual(table.size(), 1)

    def test_collision_uses_bucket_chain(self):
        table = HashMap(initial_capacity=8)
        # ord('a') % 8 == ord('i') % 8 == 1
        table.put("a", "first")
        table.put("i", "second")
        bucket_index = table._bucket_index("a")

        self.assertEqual(bucket_index, table._bucket_index("i"))
        self.assertEqual(table.buckets[bucket_index].length, 2)
        self.assertEqual(table.get("a"), "first")
        self.assertEqual(table.get("i"), "second")

    def test_load_factor_over_point_75_doubles_capacity_and_rehashes(self):
        table = HashMap(initial_capacity=4)
        table.put("a", "1")
        table.put("b", "2")
        table.put("c", "3")
        self.assertEqual(table.capacity, 4)

        table.put("d", "4")
        self.assertEqual(table.capacity, 8)
        self.assertEqual(len(table.keys()), 4)
        self.assertEqual(table.get("a"), "1")
        self.assertEqual(table.get("d"), "4")


if __name__ == "__main__":
    unittest.main()
