pentominoes = "AAAAABBB CCCDDEEB CFCDDDEB GFFHHIEE GGFHHIIJ GKFLIIMJ GKLLLMMJ KKKLMMJJ"

sequence = ['+', '+', '/', '+', '+', '+', '*', '/', '+', '+', '+', '*', '+', '+', '/', '+', '+', '+', '+', '+', '*', '+', '+', '/', '+', '+', '+', '+', '+', '*', '/', '+', '*', '/', '+', '+', '+', '+', '+', '+', '+', '+', '+', '+', '+', '+', '+', '+', '+', '+', '+', '+', '+']
nums = [0, 1, 3, 1, 5, 10, 16, 112, 14, 23, 33, 44, 528, 541, 555, 37, 53, 70, 88, 107, 127, 2667, 2689, 2712, 113, 138, 164, 191, 219, 248, 7440, 240, 272, 8976, 264, 299, 335, 372, 410, 449, 489, 530, 572, 615, 659, 704, 750, 797, 845, 894, 944, 995, 1047, 1100, 59400]
tour_spots = [(15, 0, 5), (53, 0, 7), (9, 2, 3), (25, 2, 5), (39, 4, 1), (6, 4, 4), (46, 5, 1), (18, 5, 3), (32, 5, 5), (3, 5, 6), (0, 7, 0)]
tour_indices = [k[0] for k in tour_spots]
tour_dests = [(k[1], k[2]) for k in tour_spots]

adj_k = [(2, 1), (-2, 1), (2, -1), (-2, -1), (1, 2), (-1, 2), (1, -2), (-1, -2)] # knight adjacencies
adj_t = [(2, 0), (-2, 0), (0, 2), (0, -2)] # tower adjacencies

grid = [[c for c in w] for w in pentominoes.split()] # Create grid

seq = []
towers_seen = []

def on_finish():
    finished_tour = [["--"] * 8 for i in range(8)]
    for i, (rx, cx) in enumerate(seq):
        finished_tour[rx][cx] = f"{i:02}"
    for l in finished_tour:
        print(l)

    finished_tour = [["----"] * 8 for i in range(8)]
    for i, (rx, cx) in enumerate(seq):
        finished_tour[rx][cx] = f"{nums[i]:04}"
    for l in finished_tour:
        print(l)
    
    res = 0
    for r in range(8):
        for c in range(8):
            if finished_tour[r][c] == "----":
                for dx, dy in [(1, 0), (-1, 0), (0, 1), (0, -1)]:
                    r2, c2 = r+dx, c+dy
                    if(r2 < 0 or r2 >= 8 or c2 < 0 or c2 >= 8 or finished_tour[r2][c2] == "----"):
                        continue
                    res += int(finished_tour[r2][c2])
    print(res)
                    

def dfs(move, r, c, towers_on): # current move, row, column, placing towers?
    
    if(r < 0 or r >= 8 or c < 0 or c >= 8):
        return

    if (r, c) in seq:
        return

    if move in tour_indices or (r, c) in tour_dests:
        if(move, r, c) not in tour_spots:
            return
    
    if towers_on:
        if grid[r][c] in towers_seen:
            return
        towers_seen.append(grid[r][c])
    seq.append((r, c))

    if len(towers_seen) == 13:
        print(move, r, c, seq, towers_on, towers_seen)
        on_finish()
    else:

        adjs = []

        if move >= len(sequence):
            adjs = adj_k + adj_t
        elif sequence[move] == "+":
            adjs = adj_k
        else:
            adjs = adj_t

        for dx, dy in adjs:
            r2, c2 = r+dx, c+dy
            dfs(move+1, r2, c2, towers_on ^ ((dx, dy) in adj_t))
            
    if towers_on:
        towers_seen.pop()
    seq.pop()

dfs(0, 7, 0, True)

# 0 AAAAABBB 8x8
# 1 CCCDDEEB
# 2 CFCDDDEB
# 3 GFFHHIEE
# 4 GGFHHIIJ
# 5 GKFLIIMJ
# 6 GKLLLMMJ
# 7 KKKLMMJJ
