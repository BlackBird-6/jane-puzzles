import os
import sys
import json
from flask import Flask, render_template, jsonify, request
from collections import defaultdict

script_dir = os.path.dirname(os.path.abspath(__file__))

def get_path(filename):
    return os.path.join(script_dir, filename)

app = Flask(__name__, static_url_path='/templates', static_folder='templates')

tile_words_map = defaultdict(set)
cached_grid = []
words_list = []
all_words_list = []

def load_words():
    global words_list
    if not words_list:
        try:
            with open(get_path('words.txt'), 'r', encoding='utf-8', errors='ignore') as f:
                words_list = f.read().splitlines()
        except FileNotFoundError:
            words_list = []

def build_word_map(grid, allow_reuse=False, equivalencies="", straight_only=False):
    global tile_words_map, cached_grid, all_words_list
    
    cached_grid = [row[:] for row in grid]
    tile_words_map.clear()
    load_words()
    
    ROWS = len(grid)
    if ROWS == 0: return
    COLUMNS = len(grid[0])
    
    eq_groups = []
    if equivalencies:
        for group_str in equivalencies.upper().split(','):
            group = [c.strip() for c in group_str.split('=') if c.strip()]
            if group:
                eq_groups.append(set(group))
                
    def check_equivalent(grid_char, search_char):
        if grid_char == search_char:
            return True
        for group in eq_groups:
            if grid_char in group and search_char in group:
                return True
        return False
    
    neis = [[-1, 1], [-1, 0], [-1, -1], [1, 0], [1, -1], [1, 1], [0, 1], [0, -1]]
    
    def dfs(r, c, remaining, seen, word, direction=None):
        for dr, dc in neis:
            if straight_only and direction is not None and (dr, dc) != direction:
                continue
                
            R, C = r + dr, c + dc
            if R < 0 or R >= ROWS or C < 0 or C >= COLUMNS:
                continue
            if not allow_reuse and (R, C) in seen:
                continue
            if check_equivalent(grid[R][C], remaining[0]):
                new_dir = direction if direction is not None else (dr, dc)
                if len(remaining) == 1:
                    for r_seen, c_seen in seen + [(R, C)]:
                        tile_words_map[(r_seen, c_seen)].add(word)
                    continue
                dfs(R, C, remaining[1:], seen + [(R, C)], word, new_dir)

    for word in words_list:
        word = word.upper()
        if len(word) <= 1:
            continue
            
        for r in range(ROWS):
            for c in range(COLUMNS):
                if check_equivalent(grid[r][c], word[0]):
                    dfs(r, c, word[1:], [(r, c)], word, None)
                    
    unique_words = set()
    for words in tile_words_map.values():
        unique_words.update(words)
    all_words_list = sorted(list(unique_words), key=lambda w: len(w), reverse=True)

@app.route('/')
def index():
    letters = []
    try:
        with open(get_path('letters.txt'), 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if line:
                    letters.append(list(line.upper()))
    except FileNotFoundError:
        # Fallback to some placeholder if the file is missing, but it is expected to be present.
        letters = [["?"] * 14 for _ in range(14)]
        
    if not cached_grid:
        build_word_map(letters)
        
    return render_template('index.html', grid=letters, all_words=all_words_list)

@app.route('/api/recompute', methods=['POST'])
def recompute_api():
    data = request.json or {}
    allow_reuse = data.get('reuse', False)
    equivalencies = data.get('equivalencies', '')
    straight_only = data.get('straight', False)
    
    # Use existing grid
    if not cached_grid:
        return jsonify({"success": False, "error": "No grid loaded"}), 400
        
    build_word_map(cached_grid, allow_reuse=allow_reuse, equivalencies=equivalencies, straight_only=straight_only)
    return jsonify({"success": True, "all_words": all_words_list})

@app.route('/api/tile/<int:r>/<int:c>')
def tile_api(r, c):
    words = sorted(list(tile_words_map.get((r, c), set())))
    return jsonify(words)

if __name__ == '__main__':
    app.run(debug=True, port=5000)
