import json
import os

# arr = [[3,9,9,6],[8,8,9,6],[8,8,24,24],[6,6,24,24]]

script_dir = os.path.dirname(os.path.abspath(__file__))
path = os.path.join(script_dir, 'redacted.txt') # no lookie
arr = json.loads(open(path).read())

NUM_ROWS = len(arr)
NUM_COLS = len(arr[0])

total = 0
for r in range(NUM_ROWS):
    sum = 0
    for c in range(NUM_COLS):
        sum += arr[r][c]
    print(sum)
    total += sum ** 2

for c in range(NUM_COLS):
    sum = 0
    for r in range(NUM_ROWS):
        sum += arr[r][c]
    print(sum)
    total += sum ** 2

print(total)
            