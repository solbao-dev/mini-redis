# Mini Redis


> **Redis-like in-memory key-value store built from scratch with a custom hash map, doubly linked list, and min heap.**  
> Python 내장 자료구조에 의존하지 않고 해시맵, 이중 연결 리스트, 최소 힙을 직접 구현한 Redis 스타일 인메모리 저장소

**CODYSSEY · Tool Learning · Data Structures & Algorithms**  
`Python` `Hash Map` `Doubly Linked List` `Min Heap` `LRU` `TTL` `CLI`

---

---

## Overview | 프로젝트 소개

This project implements a small Redis-like in-memory store from scratch to understand why Redis-style systems can provide fast key lookup, expiration, and memory eviction.

Redis를 단순히 사용하는 데서 그치지 않고 **빠른 조회·LRU 메모리 제거·TTL 만료가 내부 자료구조에서 어떻게 동작하는지 직접 구현하며 이해하는 것**을 목표로 했습니다. 해시맵, 이중 연결 리스트, 최소 힙을 직접 작성하고 하나의 Mini Redis로 조합했습니다.

## Core Architecture | 핵심 구조

| Data Structure | Role | 구현 목적 |
|---|---|---|
| Custom Hash Map | `key → value` storage | 평균 `O(1)` 키 조회 |
| Doubly Linked List | MRU ↔ LRU ordering | `O(1)` 노드 이동·삭제 |
| Min Heap | Earliest TTL first | 가장 빠른 만료 시각 추적 |
| TTL Map | Current expiration per key | Lazy deletion 검증 |

## Key Features | 주요 기능

- Redis-style `SET`, `GET`, `DEL`, `EXISTS`, `DBSIZE`, `KEYS`
- `CONFIG SET maxmemory` and LRU eviction
- `EXPIRE` / `TTL` with a custom min heap
- Lazy deletion for stale TTL heap entries
- UTF-8 byte-based memory accounting
- Redis-style command and OOM error handling
- Unit tests for individual data structures and integrated behavior

## Project Structure | 프로젝트 구조

```text
mini-redis/
├── linked_list.py
├── hash_map.py
├── min_heap.py
├── mini_redis.py
├── cli.py
├── test_linked_list.py
├── test_hash_map.py
├── test_min_heap.py
├── test_mini_redis.py
├── docs/
│   └── LEARNING_LOG.md
└── README.md
```

## Run | 실행 방법

Python 3.8 이상이 필요합니다.

```bash
python3 cli.py
```

전체 테스트:

```bash
python3 -m unittest -v
```

## Learning Focus | 학습 포인트

The main goal was not to reproduce production Redis, but to make the relationship between **data structures, algorithmic complexity, and observable database behavior** explicit and explainable.

실제 Redis 전체를 복제하는 것이 아니라 **자료구조 → 시간복잡도 → 실제 저장소 동작**이 어떻게 연결되는지 설명할 수 있도록 만드는 데 집중했습니다. 특히 해시 충돌과 체이닝, 리해싱, MRU/LRU 이동, 최소 힙의 `peek/push/pop`, TTL lazy deletion을 코드 수준에서 확인했습니다.

## Learning Log | 상세 학습 기록

자료구조별 구현 원리, 시간복잡도, TTL lazy deletion, LRU 동작과 평가 준비 과정은 별도의 Learning Log에 정리했습니다.

➡️ **[View Detailed Learning Log](./docs/LEARNING_LOG.md)**

---

**CODYSSEY AI All-in-One · Tool Learning**
