"""Mini Redis 명령, LRU, 메모리, TTL, 에러 처리 통합 테스트."""

import time
import unittest

from mini_redis import MiniRedis


class StringCommandTests(unittest.TestCase):
    def test_set_get_exists_dbsize_keys_and_delete(self):
        redis = MiniRedis()
        self.assertEqual(redis.execute(["SET", "name", "Alice"]), "OK")
        self.assertEqual(redis.execute(["GET", "name"]), '"Alice"')
        self.assertEqual(redis.execute(["EXISTS", "name"]), "(integer) 1")
        self.assertEqual(redis.execute(["DBSIZE"]), "(integer) 1")
        self.assertIn('"name"', redis.execute(["KEYS"]))
        self.assertEqual(redis.execute(["DEL", "name"]), "(integer) 1")
        self.assertEqual(redis.execute(["GET", "name"]), "(nil)")
        self.assertEqual(redis.execute(["KEYS"]), "(empty array)")


class MemoryAndLRUTests(unittest.TestCase):
    def test_utf8_memory_formula_and_overwrite(self):
        redis = MiniRedis()
        redis.set("가", "나")
        self.assertEqual(redis.used_memory, 6)
        redis.set("가", "다라")
        self.assertEqual(redis.used_memory, 9)

    def test_successful_get_changes_lru_eviction_target(self):
        redis = MiniRedis()
        redis.config_set_maxmemory("4")
        redis.set("a", "1")
        redis.set("b", "2")
        redis.get("a")
        redis.set("c", "3")

        self.assertEqual(redis.get("a"), '"1"')
        self.assertEqual(redis.get("b"), "(nil)")
        self.assertEqual(redis.get("c"), '"3"')
        self.assertEqual(redis.evicted_keys, 1)
        self.assertEqual(redis.used_memory, 4)

    def test_single_oversized_entry_returns_oom_without_changing_data(self):
        redis = MiniRedis()
        redis.set("a", "1")
        redis.config_set_maxmemory("3")
        result = redis.set("long", "value")

        self.assertEqual(
            result,
            "(error) OOM command not allowed when used_memory > 'maxmemory'",
        )
        self.assertEqual(redis.get("a"), '"1"')
        self.assertEqual(redis.dbsize(), "(integer) 1")

    def test_info_memory_has_required_fields(self):
        redis = MiniRedis()
        redis.config_set_maxmemory("30")
        redis.set("a", "1")
        info = redis.info_memory()
        self.assertIn("used_memory:2", info)
        self.assertIn("maxmemory:30", info)
        self.assertIn("evicted_keys:0", info)


class TTLTests(unittest.TestCase):
    def test_missing_no_expiry_and_immediate_expiry_results(self):
        redis = MiniRedis()
        self.assertEqual(redis.ttl("missing"), "(integer) -2")
        redis.set("a", "1")
        self.assertEqual(redis.ttl("a"), "(integer) -1")
        self.assertEqual(redis.expire("missing", "10"), "(integer) 0")
        self.assertEqual(redis.expire("a", "0"), "(integer) 1")
        self.assertEqual(redis.get("a"), "(nil)")

    def test_set_overwrite_clears_ttl(self):
        redis = MiniRedis()
        redis.set("a", "1")
        redis.expire("a", "10")
        redis.set("a", "2")
        self.assertEqual(redis.ttl("a"), "(integer) -1")

    def test_lazy_deletion_ignores_old_expiry_record(self):
        redis = MiniRedis()
        redis.set("a", "1")
        redis.expire("a", "1")
        redis.expire("a", "3")
        time.sleep(1.05)

        self.assertEqual(redis.get("a"), '"1"')
        self.assertIn(redis.ttl("a"), ("(integer) 1", "(integer) 2"))

    def test_expired_get_does_not_touch_lru(self):
        redis = MiniRedis()
        redis.set("a", "1")
        redis.set("b", "2")
        redis.expire("a", "0")
        self.assertEqual(redis.get("a"), "(nil)")
        self.assertFalse(redis.lru_nodes.contains("a"))


class ErrorHandlingTests(unittest.TestCase):
    def test_standard_errors(self):
        redis = MiniRedis()
        self.assertEqual(
            redis.execute(["HELLO"]),
            "(error) ERR unknown command 'HELLO'",
        )
        self.assertEqual(
            redis.execute(["GET"]),
            "(error) ERR wrong number of arguments for 'GET' command",
        )
        self.assertEqual(
            redis.execute(["CONFIG", "SET", "maxmemory", "abc"]),
            "(error) ERR value is not an integer or out of range",
        )
        self.assertEqual(redis.execute(["EXPIRE", "a", "abc"]), "(integer) 0")


if __name__ == "__main__":
    unittest.main()
