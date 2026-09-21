# Mini Redis

Python의 `dict`, `set`, `collections`, `heapq` 없이 핵심 자료구조를 직접 구현한 CLI 기반 Mini Redis입니다. 과제의 필수 범위인 String 명령, LRU 메모리 제거, TTL, Redis 스타일 에러 처리만 구현하며 네트워크·영속성·동시성·복잡 자료형은 포함하지 않습니다.

## 1. 실행 방법

Python 3.8 이상이 필요합니다.

```bash
cd mini_redis
python3 cli.py
```

종료하려면 `exit` 또는 `quit`을 입력합니다.

전체 테스트:

```bash
python3 -m unittest -v
```

파일별 테스트:

```bash
python3 -m unittest -v test_linked_list.py
python3 -m unittest -v test_hash_map.py
python3 -m unittest -v test_min_heap.py
python3 -m unittest -v test_mini_redis.py
```

## 2. 파일 구조와 역할

```text
mini_redis/
├── linked_list.py
├── hash_map.py
├── min_heap.py
├── mini_redis.py
├── cli.py
├── test_linked_list.py
├── test_hash_map.py
├── test_min_heap.py
├── test_mini_redis.py
├── 구현물설명.md
└── README.md
```

### `linked_list.py`

`Node`와 `DoublyLinkedList`를 정의합니다.

- `Node`는 `prev`, `next`, `data`를 가집니다.
- `head`는 리스트의 첫 노드, `tail`은 마지막 노드입니다.
- `insert_front`, `insert_back`, `remove_front`, `remove_back`, `remove_node`, `move_to_front`를 제공합니다.
- 특정 노드의 참조를 알고 있다는 전제에서 앞뒤 포인터만 바꾸므로 삽입·삭제·이동은 `O(1)`입니다.
- 해시맵 버킷의 체이닝과 LRU 사용 순서 양쪽에서 재사용합니다. 두 용도의 리스트 객체는 서로 별개입니다.

### `hash_map.py`

`HashEntry`와 `HashMap`을 정의합니다.

- `HashEntry`는 하나의 `key`, `value` 쌍입니다.
- `_hash`는 문자열의 각 문자를 `ord`로 숫자로 바꾸고 `hash_value = hash_value * 31 + ord(char)`로 누적합니다.
- `_bucket_index`는 `hash_value % capacity`로 버킷 번호를 계산합니다.
- 충돌한 항목은 버킷 내부의 `DoublyLinkedList`에 체이닝합니다.
- `put`, `get`, `remove`, `contains`는 평균 `O(1)`, `keys`는 `O(n)`, `size`는 `O(1)`입니다.
- 로드 팩터 `count / capacity`가 `0.75`를 초과하면 버킷을 2배로 확장하고 전 항목을 리해싱합니다.

Python `list`는 인덱스로 접근하는 고정 길이 버킷 테이블로만 사용합니다. 키 조회 기능은 직접 만든 해시 함수와 체이닝이 담당합니다.

### `min_heap.py`

`MinHeap`을 정의하며 TTL의 `(expire_at, key)`를 저장합니다.

- `peek`는 가장 이른 만료 항목을 `O(1)`에 확인합니다.
- `push`와 `pop`은 `_heapify_up`, `_heapify_down`으로 힙 규칙을 복구하며 `O(log n)`입니다.
- 부모 인덱스는 `(index - 1) // 2`, 자식 인덱스는 `2 * index + 1`, `2 * index + 2`입니다.
- 내부 배열이 가득 차면 새 고정 길이 배열을 2배 크기로 만들고 항목을 옮깁니다.
- Python `heapq`는 사용하지 않습니다.

### `mini_redis.py`

세 자료구조를 조합해 Redis 명령과 정책을 처리합니다.

| 내부 상태 | 역할 |
|---|---|
| `store` | `key → value` 실제 데이터 |
| `lru_list` | 앞은 MRU, 뒤는 LRU인 사용 순서 |
| `lru_nodes` | `key → LRU Node` 참조 |
| `ttl_map` | `key → 현재 유효한 expire_at` |
| `expiry_heap` | `(expire_at, key)` 최소 힙 |
| `used_memory` | 공식에 따른 현재 데이터 바이트 수 |
| `maxmemory` | 0이면 무제한인 메모리 제한 |
| `evicted_keys` | 메모리 제한으로 제거된 키 누계 |

주요 내부 메서드:

- `_entry_size`: UTF-8 기준 키와 값의 바이트 수 계산
- `_touch`: 성공한 `SET`/`GET`의 노드를 LRU 리스트 맨 앞으로 이동
- `_delete_key`: 데이터·메모리·LRU·TTL을 한 번에 정리
- `_purge_expired`: 최소 힙 위에서 이미 만료된 항목을 정리
- `_evict_if_needed`: 제한 이하가 될 때까지 LRU 키 제거
- `execute`: 명령과 인자 수를 검사한 뒤 각 명령 메서드로 전달

명령 인자 검사도 `dict` 없이 조건문으로 직접 처리합니다.

### `cli.py`

`mini-redis>` 프롬프트를 반복 출력하는 REPL입니다. `shlex.split`을 이용하여 `SET name "Alice Kim"`처럼 큰따옴표로 감싼 공백 포함 값을 파싱합니다. `exit`, `quit`, EOF, `Ctrl+C`로 종료할 수 있습니다.

### 테스트 파일

- `test_linked_list.py`: 포인터 연결, 앞뒤·중간 삭제, 동일 노드의 맨 앞 이동
- `test_hash_map.py`: 필수 메서드, 덮어쓰기, 실제 충돌 체이닝, 0.75 초과 리사이즈와 리해싱
- `test_min_heap.py`: push/peek/pop, 정렬 순서, 저장 배열 확장
- `test_mini_redis.py`: 명령 10개, UTF-8 메모리, LRU, OOM, TTL, lazy deletion, 에러 형식

## 3. 명령어

| 명령 | 정상 결과 |
|---|---|
| `SET key value` | `OK` |
| `GET key` | `"value"` 또는 `(nil)` |
| `DEL key` | `(integer) 1` 또는 `(integer) 0` |
| `EXISTS key` | `(integer) 1` 또는 `(integer) 0` |
| `DBSIZE` | `(integer) N` |
| `KEYS` | 번호가 붙은 전체 키 또는 `(empty array)` |
| `CONFIG SET maxmemory bytes` | `OK` |
| `INFO memory` | 메모리 3개 지표 |
| `EXPIRE key seconds` | `(integer) 1` 또는 `(integer) 0` |
| `TTL key` | 남은 초, `-1`, 또는 `-2` |

## 4. 핵심 동작 흐름

### `SET`

1. 만료된 키를 힙에서 먼저 정리합니다.
2. 새 엔트리 한 개의 크기가 `maxmemory`보다 크면 기존 상태를 바꾸지 않고 OOM을 반환합니다.
3. 기존 키이면 이전 크기를 빼고 값을 덮어쓴 뒤 기존 TTL을 제거합니다.
4. 새 엔트리 크기를 `used_memory`에 더합니다.
5. 해당 키를 LRU 리스트 맨 앞으로 이동합니다.
6. `used_memory > maxmemory`이면 리스트 뒤쪽의 LRU부터 제한 이하가 될 때까지 제거합니다.
7. 메모리 부족으로 제거할 때만 `evicted_keys`를 증가시킵니다.

### `GET`

1. 힙을 통해 만료 항목을 정리하고 대상 키의 만료 여부를 확인합니다.
2. 만료됐다면 데이터·TTL·LRU·메모리 정보를 함께 삭제하고 `(nil)`을 반환합니다.
3. 존재하지 않아도 `(nil)`을 반환합니다.
4. 살아 있는 값만 `"value"`로 반환하고 LRU 맨 앞으로 이동합니다.

### TTL과 lazy deletion

`EXPIRE a 10` 뒤에 `EXPIRE a 30`을 실행하면 힙에는 두 기록이 남을 수 있지만 `ttl_map[a]`에는 최신 만료 시각만 저장됩니다. 10초 기록이 힙 위에 올라왔을 때 `ttl_map`과 다르면 오래된 기록으로 판단해 무시합니다. `DEL`, 덮어쓰기, eviction 때도 힙 중간을 검색하지 않고 `ttl_map`만 제거하므로 힙 연산을 단순하게 유지합니다.

## 5. 메모리 규칙

과제 공식만 사용합니다.

```text
used_memory = Σ(len(utf8(key)) + len(utf8(value)))
```

예를 들어 `SET 가 나`는 한글 한 글자가 UTF-8에서 각각 3바이트이므로 총 6바이트입니다. 노드·포인터·버킷·힙 배열 같은 오버헤드는 공식에 따라 제외합니다.

`CONFIG SET maxmemory 0`은 무제한입니다. 설정 자체는 제한값만 바꾸며, 요구사항에 명시된 대로 다음 `SET` 후 초과 상태가 되면 eviction을 수행합니다.

## 6. 시간복잡도

| 작업 | 복잡도 | 이유 |
|---|---:|---|
| 연결 리스트의 알려진 노드 삽입·삭제·이동 | `O(1)` | 앞뒤 포인터만 수정 |
| 해시맵 `put/get/remove/contains` | 평균 `O(1)`, 최악 `O(n)` | 평균적으로 짧은 체인, 최악에는 한 버킷에 집중 |
| 해시맵 `keys` | `O(n)` | 모든 항목 방문 |
| 해시맵 리사이즈 | `O(n)` | 모든 항목 리해싱 |
| LRU 조회+갱신 | 평균 `O(1)` | 해시맵으로 노드 조회 + 리스트 이동 |
| 힙 `peek` | `O(1)` | 루트 확인 |
| 힙 `push/pop` | `O(log n)` | 트리 높이만큼 이동 |
| `DBSIZE` | `O(1)` | 해시맵의 `count` 반환(만료 정리 비용 제외) |
| `KEYS` | `O(n)` | 모든 키 출력 |

문자열 키 자체를 해시하는 비용은 키 길이를 `k`라 할 때 `O(k)`입니다. 해시맵 조회가 평균 `O(1)`이라는 설명은 전체 저장 항목 수 `n`에 대한 표현입니다.

## 7. 에러 형식

```text
(error) ERR unknown command '<cmd>'
(error) ERR wrong number of arguments for '<CMD>' command
(error) ERR value is not an integer or out of range
(error) OOM command not allowed when used_memory > 'maxmemory'
```

## 8. 제약 준수표

| 미션 요구 | 구현 |
|---|---|
| 이중 연결 리스트 직접 구현 | `linked_list.py` |
| 체이닝 해시맵·직접 해시 함수·0.75 리사이즈 | `hash_map.py` |
| 최소 힙·heapify 직접 구현 | `min_heap.py` |
| 자료구조별 독립 파일 | 준수 |
| 핵심 주석/docstring | 각 소스 파일에 작성 |
| `dict`, `set`, `collections` 금지 | 사용하지 않음 |
| 내장 해시맵·캐시 대체 금지 | 직접 만든 `HashMap` 사용 |
| 네트워크·영속성·복잡 자료형·동시성 제외 | 준수 |
| Python 3.8 이상 | 호환 문법 사용 |

보너스인 Pub/Sub, BST 등은 필수 범위의 정확성과 설명 가능성에 집중하기 위해 포함하지 않았습니다.

구현물 설명과 동료평가 시연 및 예상 질문 답변은 [`구현물설명.md`](구현물설명.md)를 따릅니다.
