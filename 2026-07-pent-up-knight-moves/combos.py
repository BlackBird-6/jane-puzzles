nums = [0, 1, 16, 23, 37, 88, 138, 272, 449, 528, 750, 1100]

# + * /
K = 7

def dfs(n, move, nums_seen, operations):
    global K
    # print(n, move, operations, nums_seen)

    nums_to_add = []

    # 3 6 9 12 15 18 21 24
    if (move <= 19 and move % 3 == 1) or (move > 19 and (move-18) % K == 1): # after move 0, 3, 6...
        if n not in nums or n in nums_seen:
            return
        nums_to_add.append(n)
        
    if move == 19 + 5*K: # End state
        print(operations)
        return

    dfs(n + move, move+1, nums_seen + nums_to_add, operations + [f'+{move} ({n+move})'])
    dfs(n * move, move+1, nums_seen + nums_to_add, operations + [f'*{move} ({n*move})'])
    if n % move == 0:
        dfs(int(n/move), move+1, nums_seen + nums_to_add, operations + [f'/{move} ({n/move})'])

for i in range(1, 10):
    K = i
    print(f"K = {K}")
    dfs(0, 1, [], []) # start entering move 1
