"""Command-line REPL for Mini Redis."""

import shlex

from mini_redis import MiniRedis


def main():
    redis = MiniRedis()
    while True:
        try:
            line = input("mini-redis> ")
        except (EOFError, KeyboardInterrupt):
            print()
            break

        line = line.strip()
        if not line:
            continue
        if line.lower() in ("exit", "quit"):
            break

        try:
            tokens = shlex.split(line)
        except ValueError:
            print("(error) ERR invalid quoted string")
            continue
        print(redis.execute(tokens))


if __name__ == "__main__":
    main()
