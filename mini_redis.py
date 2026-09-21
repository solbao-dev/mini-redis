"""String 명령, LRU, 메모리 제한, TTL을 조합한 Mini Redis 핵심 로직."""

import math
import time

from hash_map import HashMap
from linked_list import DoublyLinkedList
from min_heap import MinHeap


class MiniRedis:
    """직접 만든 자료구조들을 조합하여 Redis 스타일 명령을 처리한다."""
    def __init__(self):
        self.store = HashMap()
        self.lru_list = DoublyLinkedList()
        self.lru_nodes = HashMap()
        self.ttl_map = HashMap()
        self.expiry_heap = MinHeap()
        self.used_memory = 0
        self.maxmemory = 0
        self.evicted_keys = 0

    @staticmethod
    def _entry_size(key, value):
        return len(key.encode("utf-8")) + len(value.encode("utf-8"))

    def _delete_key(self, key, count_as_eviction=False):
        value = self.store.get(key)
        if value is None and not self.store.contains(key):
            return False

        self.used_memory -= self._entry_size(key, value)
        self.store.remove(key)

        node = self.lru_nodes.get(key)
        if node is not None:
            self.lru_list.remove_node(node)
            self.lru_nodes.remove(key)

        self.ttl_map.remove(key)
        if count_as_eviction:
            self.evicted_keys += 1
        return True

    def _touch(self, key):
        node = self.lru_nodes.get(key)
        if node is not None:
            self.lru_list.move_to_front(node)
            return
        new_node = self.lru_list.insert_front(key)
        self.lru_nodes.put(key, new_node)

    def _purge_expired(self):
        now = time.monotonic()
        while self.expiry_heap.peek() is not None:
            expire_at, key = self.expiry_heap.peek()
            if expire_at > now:
                break
            self.expiry_heap.pop()
            current_expire_at = self.ttl_map.get(key)
            if current_expire_at is None:
                continue
            if current_expire_at == expire_at:
                self._delete_key(key)

    def _expire_if_needed(self, key):
        self._purge_expired()
        expire_at = self.ttl_map.get(key)
        if expire_at is not None and expire_at <= time.monotonic():
            self._delete_key(key)
            return True
        return False

    def _evict_if_needed(self):
        while self.maxmemory > 0 and self.used_memory > self.maxmemory:
            key = self.lru_list.tail.data if self.lru_list.tail else None
            if key is None:
                break
            self._delete_key(key, count_as_eviction=True)

    def set(self, key, value):
        self._purge_expired()
        new_size = self._entry_size(key, value)
        if self.maxmemory > 0 and new_size > self.maxmemory:
            return "(error) OOM command not allowed when used_memory > 'maxmemory'"

        old_value = self.store.get(key)
        if old_value is not None or self.store.contains(key):
            self.used_memory -= self._entry_size(key, old_value)
            self.store.put(key, value)
            self.ttl_map.remove(key)
        else:
            self.store.put(key, value)

        self.used_memory += new_size
        self._touch(key)
        self._evict_if_needed()
        return "OK"

    def get(self, key):
        if self._expire_if_needed(key):
            return "(nil)"
        value = self.store.get(key)
        if value is None and not self.store.contains(key):
            return "(nil)"
        self._touch(key)
        return '"' + value + '"'

    def delete(self, key):
        self._purge_expired()
        return "(integer) 1" if self._delete_key(key) else "(integer) 0"

    def exists(self, key):
        if self._expire_if_needed(key):
            return "(integer) 0"
        return "(integer) 1" if self.store.contains(key) else "(integer) 0"

    def dbsize(self):
        self._purge_expired()
        return "(integer) " + str(self.store.size())

    def keys(self):
        self._purge_expired()
        keys = self.store.keys()
        if not keys:
            return "(empty array)"
        return "\n".join(str(i + 1) + '. "' + key + '"' for i, key in enumerate(keys))

    def config_set_maxmemory(self, value):
        try:
            parsed = int(value)
        except (TypeError, ValueError):
            return "(error) ERR value is not an integer or out of range"
        if parsed < 0:
            return "(error) ERR value is not an integer or out of range"
        self.maxmemory = parsed
        return "OK"

    def info_memory(self):
        return (
            "used_memory:" + str(self.used_memory) + "\n"
            "maxmemory:" + str(self.maxmemory) + "\n"
            "evicted_keys:" + str(self.evicted_keys)
        )

    def expire(self, key, seconds):
        self._purge_expired()
        if not self.store.contains(key):
            return "(integer) 0"
        try:
            parsed = int(seconds)
        except (TypeError, ValueError):
            return "(error) ERR value is not an integer or out of range"
        if parsed <= 0:
            self._delete_key(key)
            return "(integer) 1"
        expire_at = time.monotonic() + parsed
        self.ttl_map.put(key, expire_at)
        self.expiry_heap.push((expire_at, key))
        return "(integer) 1"

    def ttl(self, key):
        if self._expire_if_needed(key):
            return "(integer) -2"
        if not self.store.contains(key):
            return "(integer) -2"
        expire_at = self.ttl_map.get(key)
        if expire_at is None:
            return "(integer) -1"
        remaining = max(0, math.ceil(expire_at - time.monotonic()))
        return "(integer) " + str(remaining)

    def execute(self, tokens):
        if not tokens:
            return ""
        command = tokens[0].upper()
        arguments = tokens[1:]
        if command == "SET":
            if len(arguments) != 2:
                return self._wrong_number(command)
            return self.set(arguments[0], arguments[1])
        if command == "GET":
            if len(arguments) != 1:
                return self._wrong_number(command)
            return self.get(arguments[0])
        if command == "DEL":
            if len(arguments) != 1:
                return self._wrong_number(command)
            return self.delete(arguments[0])
        if command == "EXISTS":
            if len(arguments) != 1:
                return self._wrong_number(command)
            return self.exists(arguments[0])
        if command == "DBSIZE":
            if len(arguments) != 0:
                return self._wrong_number(command)
            return self.dbsize()
        if command == "KEYS":
            if len(arguments) != 0:
                return self._wrong_number(command)
            return self.keys()
        if command == "EXPIRE":
            if len(arguments) != 2:
                return self._wrong_number(command)
            return self.expire(arguments[0], arguments[1])
        if command == "TTL":
            if len(arguments) != 1:
                return self._wrong_number(command)
            return self.ttl(arguments[0])
        if command == "INFO":
            if len(arguments) != 1:
                return self._wrong_number(command)
            if arguments[0].lower() != "memory":
                return "(error) ERR unsupported INFO section"
            return self.info_memory()
        if command == "CONFIG":
            if len(arguments) != 3:
                return self._wrong_number(command)
            if arguments[0].upper() != "SET" or arguments[1].lower() != "maxmemory":
                return "(error) ERR unsupported CONFIG command"
            return self.config_set_maxmemory(arguments[2])
        return "(error) ERR unknown command '" + tokens[0] + "'"

    @staticmethod
    def _wrong_number(command):
        return "(error) ERR wrong number of arguments for '" + command + "' command"
