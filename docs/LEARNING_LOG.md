# Mini Redis — Learning Log

> CODYSSEY Data Structures & Algorithms 미션에서 Mini Redis를 구현하며 정리한 상세 구현·평가 준비 기록입니다.

## Mission Constraints | 구현 규칙

Python의 `dict`, `set`, `collections`, `heapq` 없이 핵심 자료구조를 직접 구현한 CLI 기반 Mini Redis입니다. 과제의 필수 범위인 String 명령, LRU 메모리 제거, TTL, Redis 스타일 에러 처리만 구현하며 네트워크·영속성·동시성·복잡 자료형은 포함하지 않습니다.

## Data Structures | 자료구조

### Doubly Linked List

`Node`와 `DoublyLinkedList`를 직접 구현했습니다.

- `Node`: `prev`, `next`, `data`
- `head`: 첫 노드
- `tail`: 마지막 노드
- `insert_front`, `insert_back`, `remove_front`, `remove_back`, `remove_node`, `move_to_front`
- 특정 노드 참조를 알고 있을 때 삽입·삭제·이동은 `O(1)`
- 해시맵 체이닝과 LRU 사용 순서에 각각 별도 리스트를 사용

### Custom Hash Map

`HashEntry`와 `HashMap`을 직접 구현했습니다.

- 문자열 문자를 `ord`로 변환하여 `hash_value = hash_value * 31 + ord(char)`로 누적
- `hash_value % capacity`로 버킷 계산
- 충돌은 버킷 내부 이중 연결 리스트 체이닝으로 처리
- `put`, `get`, `remove`, `contains`: 평균 `O(1)`
- `keys`: `O(n)`
- `size`: `O(1)`
- 로드 팩터가 `0.75`를 초과하면 capacity를 2배로 확장하고 리해싱

Python `list`는 고정 길이 버킷 테이블로만 사용하며 키 조회 기능은 직접 만든 해시 함수와 체이닝이 담당합니다.

### Min Heap

TTL의 `(expire_at, key)`를 저장하는 `MinHeap`을 직접 구현했습니다.

- `peek`: 가장 이른 만료 항목 확인 `O(1)`
- `push`, `pop`: `O(log n)`
- 부모: `(index - 1) // 2`
- 왼쪽 자식: `2 * index + 1`
- 오른쪽 자식: `2 * index + 2`
- 배열이 가득 차면 2배 크기로 확장
- Python `heapq` 미사용

## Mini Redis Internal State | 내부 상태

| State | Role |
|---|---|
| `store` | `key → value` 실제 데이터 |
| `lru_list` | 앞은 MRU, 뒤는 LRU인 사용 순서 |
| `lru_nodes` | `key → LRU Node` 참조 |
| `ttl_map` | `key → 현재 유효한 expire_at` |
| `expiry_heap` | `(expire_at, key)` 최소 힙 |
| `used_memory` | 현재 데이터 바이트 수 |
| `maxmemory` | 메모리 제한, 0이면 무제한 |
| `evicted_keys` | 메모리 제한으로 제거된 키 누계 |

주요 내부 메서드:

- `_entry_size`: UTF-8 기준 키와 값의 바이트 수 계산
- `_touch`: 성공한 `SET`/`GET`을 MRU로 이동
- `_delete_key`: 데이터·메모리·LRU·TTL 정리
- `_purge_expired`: 만료 항목 정리
- `_evict_if_needed`: 제한 이하가 될 때까지 LRU 키 제거
- `execute`: 명령과 인자 검사 후 실행

## TTL & Lazy Deletion | TTL과 지연 삭제

TTL을 갱신할 때 기존 힙 항목을 중간에서 직접 찾아 제거하지 않고 새 만료 정보를 힙에 추가합니다. `ttl_map[key]`에는 현재 유효한 만료 시각만 유지합니다.

오래된 힙 항목이 루트로 올라왔을 때 `ttl_map`의 현재 값과 비교하여 일치하지 않으면 stale entry로 판단해 무시합니다. 이 방식으로 힙 중간 삭제의 복잡성을 피했습니다.

## LRU | 메모리 제거 정책

LRU 리스트의 앞쪽은 MRU(Most Recently Used), 뒤쪽은 LRU(Least Recently Used)로 유지합니다. 성공한 `SET` 또는 `GET` 시 해당 노드를 앞쪽으로 이동하고, 메모리 제한을 초과하면 tail의 가장 오래 사용하지 않은 키부터 제거합니다.

## Complexity | 시간복잡도

| Operation | Complexity |
|---|---:|
| Hash Map lookup | Average `O(1)` |
| LRU node move/remove | `O(1)` |
| Min Heap `peek` | `O(1)` |
| Min Heap `push/pop` | `O(log n)` |
| `KEYS` | `O(n)` |

## Testing | 테스트

- `test_linked_list.py`: 포인터 연결, 앞뒤·중간 삭제, 동일 노드 이동
- `test_hash_map.py`: 덮어쓰기, 충돌 체이닝, resize/rehash
- `test_min_heap.py`: push/peek/pop, 정렬 순서, 배열 확장
- `test_mini_redis.py`: 명령, UTF-8 메모리, LRU, OOM, TTL, lazy deletion, 에러 형식

## What I Learned | 배운 점

이 미션의 핵심은 Redis API를 흉내 내는 것보다 **자료구조가 실제 시스템 동작으로 어떻게 연결되는지 설명할 수 있게 된 것**입니다.

해시맵은 빠른 키 조회, 이중 연결 리스트는 LRU의 `O(1)` 이동·삭제, 최소 힙은 가장 가까운 TTL 만료를 효율적으로 찾는 역할을 담당합니다. 각각의 자료구조를 따로 배우는 것에서 나아가 하나의 저장 시스템 안에서 조합해보며 시간복잡도와 설계 선택의 이유를 이해했습니다.
