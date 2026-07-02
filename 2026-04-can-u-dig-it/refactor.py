import os
import re

script_path = os.path.join("templates", "script.js")

with open(script_path, "r", encoding="utf-8") as f:
    content = f.read()

# 1. Remove the old renderAllWords(allWords) call at top
content = re.sub(r'renderAllWords\(allWords\);\s*', '', content)

# 2. Add buildWordMap function
build_word_map_js = """
let tileWordsMap = {};
let wordsList = [];
let allWords = [];
let gridData = [];
const rows = 14;
const cols = 14;

async function buildWordMap() {
    tileWordsMap = {};
    for (let r = 0; r < rows; r++) {
        for (let c = 0; c < cols; c++) {
            tileWordsMap[`${r},${c}`] = new Set();
        }
    }
    
    const allowReuse = reuseToggle.checked;
    const straightOnly = straightToggle.checked;
    
    function dfs(r, c, remaining, seen, word, direction) {
        for (let d of dirs) {
            if (straightOnly && direction !== null && (direction[0] !== d[0] || direction[1] !== d[1])) continue;
            let nr = r + d[0];
            let nc = c + d[1];
            if (nr >= 0 && nr < rows && nc >= 0 && nc < cols) {
                if (!allowReuse && seen.some(pos => pos[0] === nr && pos[1] === nc)) continue;
                
                if (checkEquivalent(gridData[nr][nc], remaining[0])) {
                    let newDir = direction !== null ? direction : d;
                    if (remaining.length === 1) {
                        for (let pos of seen) {
                            tileWordsMap[`${pos[0]},${pos[1]}`].add(word);
                        }
                        tileWordsMap[`${nr},${nc}`].add(word);
                    } else {
                        seen.push([nr, nc]);
                        dfs(nr, nc, remaining.slice(1), seen, word, newDir);
                        seen.pop();
                    }
                }
            }
        }
    }

    // Process in chunks to avoid freezing the UI
    return new Promise(resolve => {
        let uniqueWords = new Set();
        let i = 0;
        const chunkSize = 1000;
        
        function processChunk() {
            const end = Math.min(i + chunkSize, wordsList.length);
            for (; i < end; i++) {
                const word = wordsList[i];
                if (word.length <= 1) continue;
                for (let r = 0; r < rows; r++) {
                    for (let c = 0; c < cols; c++) {
                        if (checkEquivalent(gridData[r][c], word[0])) {
                            dfs(r, c, word.slice(1), [[r, c]], word, null);
                        }
                    }
                }
            }
            if (i < wordsList.length) {
                setTimeout(processChunk, 0);
            } else {
                for (let key in tileWordsMap) {
                    for (let word of tileWordsMap[key]) uniqueWords.add(word);
                }
                allWords = Array.from(uniqueWords).sort((a, b) => b.length - a.length);
                renderAllWords(allWords);
                resolve();
            }
        }
        processChunk();
    });
}
"""

content = content.replace("function checkEquivalent", build_word_map_js + "\nfunction checkEquivalent")

# 3. Replace btnRecompute click
btn_recompute_old = """btnRecompute.addEventListener('click', async () => {
    btnRecompute.disabled = true;
    recomputeStatus.style.display = 'block';
    try {
        const response = await fetch('/api/recompute', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                reuse: reuseToggle.checked,
                equivalencies: equivInput.value,
                straight: straightToggle.checked
            })
        });
        const data = await response.json();
        if (!data.success) {
            alert('Recompute failed: ' + data.error);
        } else {
            document.getElementById('selectedTileSection').style.display = 'none';
            renderAllWords(data.all_words);
        }
    } catch (err) {
        console.error(err);
        alert('An error occurred during recompute.');
    } finally {
        btnRecompute.disabled = false;
        recomputeStatus.style.display = 'none';
    }
});"""

btn_recompute_new = """btnRecompute.addEventListener('click', async () => {
    btnRecompute.disabled = true;
    recomputeStatus.style.display = 'block';
    
    // allow UI to render status
    await new Promise(r => setTimeout(r, 50));
    
    try {
        await buildWordMap();
        document.getElementById('selectedTileSection').style.display = 'none';
    } catch (err) {
        console.error(err);
        alert('An error occurred during recompute.');
    } finally {
        btnRecompute.disabled = false;
        recomputeStatus.style.display = 'none';
    }
});"""
content = content.replace(btn_recompute_old, btn_recompute_new)

# 4. Replace API call in tile click
tile_api_old = """        try {
            const response = await fetch(`/api/tile/${r}/${c}`);
            let words = await response.json();"""

tile_api_new = """        try {
            let words = Array.from(tileWordsMap[`${r},${c}`] || []).sort();"""

content = content.replace(tile_api_old, tile_api_new)


# 5. Remove 'let tilesMap = []; ...' initialization from middle, wrap it into an init function

init_js = """
async function init() {
    try {
        const wRes = await fetch('../words.txt');
        const wText = await wRes.text();
        wordsList = wText.split('\\n').map(w => w.trim().toUpperCase()).filter(w => w);
        
        const lRes = await fetch('../letters.txt');
        const lText = await lRes.text();
        const lLines = lText.split('\\n').map(l => l.trim().toUpperCase()).filter(l => l);
        
        gridData = [];
        for (let r = 0; r < rows; r++) {
            if (lLines[r]) {
                gridData.push(lLines[r].split(''));
            } else {
                gridData.push(Array(cols).fill('?'));
            }
        }
        
        letterGrid.innerHTML = '';
        tilesMap = [];
        for (let r = 0; r < rows; r++) {
            let rowArr = [];
            for (let c = 0; c < cols; c++) {
                const tile = document.createElement('div');
                tile.className = 'tile';
                tile.dataset.r = r;
                tile.dataset.c = c;
                tile.textContent = gridData[r][c];
                letterGrid.appendChild(tile);
                rowArr.push(tile);
            }
            tilesMap.push(rowArr);
        }
        
        setupTileListeners();
        
        recomputeStatus.style.display = 'block';
        recomputeStatus.textContent = 'Loading words...';
        await buildWordMap();
        recomputeStatus.style.display = 'none';
        recomputeStatus.textContent = 'Computing... Please wait';
        
    } catch (err) {
        console.error("Init error", err);
    }
}
"""

content = content + "\\n" + init_js + "\\ninit();\\n"

# Need to replace the old tile initialization and listener attachment with setupTileListeners
old_init_tiles = """let tilesMap = []; // 2D array of DOM elements

// Initialize tilesMap
const tileEls = document.querySelectorAll('.tile');
let idx = 0;
for (let r = 0; r < rows; r++) {
    let rowArr = [];
    for (let c = 0; c < cols; c++) {
        rowArr.push(tileEls[idx]);
        idx++;
    }
    tilesMap.push(rowArr);
}"""

content = content.replace(old_init_tiles, "")

old_listener_start = """// Tile click logic
window.actualSearchValue = searchInput.value;
window.isHoveringWord = false;
window.selectedCells = [];

tileEls.forEach(tile => {"""

new_listener_start = """// Tile click logic
window.actualSearchValue = searchInput.value;
window.isHoveringWord = false;
window.selectedCells = [];

function setupTileListeners() {
    const tileEls = document.querySelectorAll('.tile');
    tileEls.forEach(tile => {"""

content = content.replace(old_listener_start, new_listener_start)

old_listener_end = """        } catch (e) {
            console.error('Error fetching tile words:', e);
        }
    });
});"""

new_listener_end = """        } catch (e) {
            console.error('Error fetching tile words:', e);
        }
    });
});
}"""

content = content.replace(old_listener_end, new_listener_end)

with open(script_path, "w", encoding="utf-8") as f:
    f.write(content)
