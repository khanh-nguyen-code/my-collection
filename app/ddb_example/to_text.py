import json
import sys

if __name__ == "__main__":
    s = sys.stdin.read()
    o = json.loads(s)
    keys = list(map(lambda key: int(key.split("_")[1]), o.keys()))
    keys.sort()
    for k in keys:
        key = f"line_{k}"
        sys.stdout.write(o[key] + "\n")


