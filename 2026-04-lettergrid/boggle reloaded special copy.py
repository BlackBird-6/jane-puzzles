import pyautogui
import time
import copy

str = "e"
print(str + "a")

# input = input("What grid would you like to input? ").split("/")
input = "rsdifindthsart/ehresodaeetgna/netrhalxhgowip/egedauyueaenrp/ptnnmllmxidnee/ohuinkthanacsm/alnpfyldebsttn/uumjarebemehrw/mithdceigiugts/tlamibftoteget/sailniitniapen/nstoagrniiobrt/ietiryeesprayw/tunenty-tessix".upper().split("/")


grid = [[c for c in l] for l in input]
print(grid)

words = open("words.txt", "r+").read().splitlines()
res = []

neis = [[-1, 1], [-1, 0], [-1, -1], [1, 0], [1, -1], [1, 1], [0, 1], [0, -1]]
ROWS = len(grid)
COLUMNS = len(grid[0])

def dfs(r, c, remaining, seen, word):
    for dr, dc in neis:
        R, C = r+dr, c+dc

        if R < 0 or R >= ROWS or C < 0 or C >= COLUMNS:
            continue

        if (R, C) in seen:
            continue

        if grid[R][C] == remaining[0]:

            if len(remaining) == 1:
                res.append(word)

                grid_sim = copy.deepcopy(grid)
                seen.append((R, C))
                for (R, C) in seen:
                    grid_sim[R][C] = "-"

                print(word)
                for R in grid_sim:
                    print("".join(R))
                print("")

                return

            dfs(R, C, remaining[1:], seen + [(R, C)], word)

for word in words:
    word = word.upper()

    # if len(word) <= 3:
    #     continue

    seen = []

    for r in range(ROWS):
        for c in range(COLUMNS):
            if grid[r][c] == word[0]:
                dfs(r, c, word[1:], [(r, c)], word)

# remove dupes
res = list(set(res))
res.sort(key=lambda s: len(s), reverse=True)
print(res)
print(len(res))

# time.sleep(3)
# for r in res:
#     pyautogui.write(r)
#     pyautogui.press('enter')
#     pyautogui.press('esc')