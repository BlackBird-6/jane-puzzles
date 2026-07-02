const searchInput = document.getElementById('searchInput');
const colorPicker = document.getElementById('colorPicker');
const btnSave = document.getElementById('btnSave');
const svgOverlay = document.getElementById('svgOverlay');
const letterGrid = document.getElementById('letterGrid');
const savedQueriesList = document.getElementById('savedQueriesList');
const equivInput = document.getElementById('equivInput');
const reuseToggle = document.getElementById('reuseToggle');
const straightToggle = document.getElementById('straightToggle');
const showLinesToggle = document.getElementById('showLinesToggle');
const btnRecompute = document.getElementById('btnRecompute');
const recomputeStatus = document.getElementById('recomputeStatus');
const allWordsListEl = document.getElementById('allWordsList');
const allWordsCountEl = document.getElementById('allWordsCount');

let savedQueries = JSON.parse(localStorage.getItem('letterGridQueries') || '[]');
equivInput.value = localStorage.getItem('letterGridEquiv') || '';
reuseToggle.checked = localStorage.getItem('letterGridReuse') === 'true';
straightToggle.checked = localStorage.getItem('letterGridStraight') === 'true';
showLinesToggle.checked = localStorage.getItem('letterGridShowLines') !== 'false';

equivInput.addEventListener('input', () => {
    localStorage.setItem('letterGridEquiv', equivInput.value);
    handleSearch();
    renderSavedQueries();
});

reuseToggle.addEventListener('change', () => {
    localStorage.setItem('letterGridReuse', reuseToggle.checked);
    handleSearch();
    renderSavedQueries();
});

straightToggle.addEventListener('change', () => {
    localStorage.setItem('letterGridStraight', straightToggle.checked);
    handleSearch();
    renderSavedQueries();
});

showLinesToggle.addEventListener('change', () => {
    localStorage.setItem('letterGridShowLines', showLinesToggle.checked);
    drawPaths();
});

btnRecompute.addEventListener('click', async () => {
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
});

function renderAllWords(words) {
    allWordsCountEl.textContent = `(${words.length})`;
    allWordsListEl.innerHTML = '';
    words.forEach(word => {
        const pill = document.createElement('div');
        pill.className = 'all-word-pill';
        pill.textContent = word;
        pill.addEventListener('click', () => {
            searchInput.value = word;
            handleSearch();
        });
        pill.addEventListener('mouseenter', () => {
            window.isHoveringWord = true;
            searchInput.value = word;
            handleSearch();
        });
        pill.addEventListener('mouseleave', () => {
            window.isHoveringWord = false;
            setTimeout(() => {
                if (!window.isHoveringWord) {
                    searchInput.value = window.actualSearchValue;
                    handleSearch();
                }
            }, 50);
        });
        allWordsListEl.appendChild(pill);
    });
}

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

function checkEquivalent(gridLetter, searchLetter) {
    if (gridLetter === searchLetter) return true;

    const eqStr = equivInput.value.trim().toUpperCase();
    if (!eqStr) return false;

    const groups = eqStr.split(',').map(s => s.split('=').map(c => c.trim()).filter(c => c));
    for (let g of groups) {
        if (g.includes(gridLetter) && g.includes(searchLetter)) {
            return true;
        }
    }
    return false;
}



// Search variables
let currentPaths = []; // Array of paths (each path is an array of [r, c] coordinates)

// Adjacency directions (8-way)
const dirs = [
    [-1, -1], [-1, 0], [-1, 1],
    [0, -1], [0, 1],
    [1, -1], [1, 0], [1, 1]
];

function findPaths(word) {
    if (!word) return [];
    word = word.toUpperCase();
    let allPaths = [];

    function dfs(r, c, index, path, visited, direction) {
        if (index === word.length) {
            allPaths.push([...path]);
            return true;
        }
        let foundAny = false;
        for (let d of dirs) {
            if (straightToggle.checked && direction !== null && (direction[0] !== d[0] || direction[1] !== d[1])) {
                continue;
            }

            let nr = r + d[0], nc = c + d[1];
            if (nr >= 0 && nr < rows && nc >= 0 && nc < cols) {
                const canVisit = reuseToggle.checked ? true : !visited[nr][nc];
                if (canVisit && checkEquivalent(gridData[nr][nc], word[index])) {
                    let newDir = direction !== null ? direction : d;
                    let wasVisited = visited[nr][nc];
                    visited[nr][nc] = true;
                    path.push([nr, nc]);
                    let found = dfs(nr, nc, index + 1, path, visited, newDir);
                    if (found) foundAny = true;
                    path.pop();
                    visited[nr][nc] = wasVisited;
                }
            }
        }
        return foundAny;
    }

    for (let r = 0; r < rows; r++) {
        for (let c = 0; c < cols; c++) {
            if (checkEquivalent(gridData[r][c], word[0])) {
                let visited = Array.from({ length: rows }, () => Array(cols).fill(false));
                visited[r][c] = true;
                dfs(r, c, 1, [[r, c]], visited, null);
            }
        }
    }
    return allPaths;
}

function drawPaths() {
    svgOverlay.innerHTML = '';

    // Re-apply box-shadow/color to active tiles
    document.querySelectorAll('.tile.active').forEach(t => t.classList.remove('active'));
    document.querySelectorAll('.tile.selected').forEach(t => t.classList.remove('selected'));
    document.querySelectorAll('.tile').forEach(t => t.style.background = '');

    let stuffToDraw = [];
    if (currentPaths.length > 0) {
        stuffToDraw.push({ paths: currentPaths, color: colorPicker.value });
    }

    savedQueries.forEach(q => {
        if (q.visible) {
            if (q.type === 'group') {
                stuffToDraw.push({ paths: [q.cells], color: q.color, noLines: true });
            } else {
                const qPaths = findPaths(q.word);
                if (qPaths.length > 0) {
                    stuffToDraw.push({ paths: qPaths, color: q.color });
                }
            }
        }
    });

    if (window.selectedCells && window.selectedCells.length > 0) {
        stuffToDraw.push({ paths: [window.selectedCells], color: colorPicker.value, noLines: true, isSelection: true });
    }

    if (stuffToDraw.length === 0) return;

    const gridRect = letterGrid.getBoundingClientRect();

    stuffToDraw.forEach(item => {
        item.paths.forEach(path => {
            let dStr = '';
            path.forEach((pos, idx) => {
                const r = pos[0], c = pos[1];
                const tile = tilesMap[r][c];
                tile.classList.add('active');
                if (item.isSelection) tile.classList.add('selected');
                tile.style.background = item.color;

                const tRect = tile.getBoundingClientRect();
                const x = tRect.left - gridRect.left + tRect.width / 2;
                const y = tRect.top - gridRect.top + tRect.height / 2;

                if (idx === 0) {
                    dStr += `M ${x} ${y} `;
                } else {
                    dStr += `L ${x} ${y} `;
                }
            });

            if (showLinesToggle.checked && !item.noLines && path.length > 1) {
                const pathEl = document.createElementNS("http://www.w3.org/2000/svg", "path");
                pathEl.setAttribute('d', dStr);
                pathEl.setAttribute('class', 'line-path');
                pathEl.setAttribute('stroke', item.color);
                svgOverlay.appendChild(pathEl);
            }
        });
    });
}

function handleSearch() {
    const word = searchInput.value.trim();
    currentPaths = findPaths(word);
    drawPaths();
}

searchInput.addEventListener('input', () => {
    window.actualSearchValue = searchInput.value;
    handleSearch();
});
colorPicker.addEventListener('input', drawPaths); // Redraw paths changing color in realtime

window.addEventListener('resize', () => {
    // Give DOM a tick to layout
    setTimeout(drawPaths, 50);
});

// Tile click logic
window.actualSearchValue = searchInput.value;
window.isHoveringWord = false;
window.selectedCells = [];

function setupTileListeners() {
    const tileEls = document.querySelectorAll('.tile');
    tileEls.forEach(tile => {
    tile.style.cursor = 'pointer';
    tile.addEventListener('click', async (e) => {
        const r = parseInt(tile.dataset.r);
        const c = parseInt(tile.dataset.c);
        const letter = tile.textContent;

        if (e.ctrlKey) {
            const idx = window.selectedCells.findIndex(pos => pos[0] === r && pos[1] === c);
            if (idx > -1) {
                window.selectedCells.splice(idx, 1);
            } else {
                window.selectedCells.push([r, c]);
            }
            drawPaths();
            return;
        }

        window.selectedCells = [];
        drawPaths();

        try {
            let words = Array.from(tileWordsMap[`${r},${c}`] || []).sort();

            // Prioritize words that start with this tile's letter
            const startsWith = words.filter(w => w.startsWith(letter));
            const others = words.filter(w => !w.startsWith(letter));
            words = [...startsWith, ...others];

            document.getElementById('selectedTileSection').style.display = 'block';
            document.getElementById('selectedTileHeader').textContent = `Words through ${letter} (${r},${c})`;

            const ul = document.getElementById('selectedTileWords');
            ul.innerHTML = '';

            if (words.length === 0) {
                ul.innerHTML = '<li class="saved-query"><div class="query-text">No words found</div></li>';
            }

            words.forEach(word => {
                const li = document.createElement('li');
                li.className = 'saved-query';
                li.innerHTML = `<div class="query-text">${word}</div>`;

                li.addEventListener('mouseenter', () => {
                    window.isHoveringWord = true;
                    searchInput.value = word;
                    handleSearch();
                });

                li.addEventListener('mouseleave', () => {
                    window.isHoveringWord = false;
                    setTimeout(() => {
                        if (!window.isHoveringWord) {
                            searchInput.value = window.actualSearchValue;
                            handleSearch();
                        }
                    }, 10);
                });

                li.addEventListener('click', () => {
                    window.actualSearchValue = word;
                    searchInput.value = word;
                    handleSearch();
                });

                ul.appendChild(li);
            });
        } catch (e) {
            console.error('Error fetching tile words:', e);
        }
    });
});
}

// Save Query Logic
function renderSavedQueries() {
    savedQueriesList.innerHTML = '';
    savedQueries.forEach((q, index) => {
        const li = document.createElement('li');
        li.className = 'saved-query';

        let isNotFound = false;
        if (q.type !== 'group') {
            const paths = findPaths(q.word);
            isNotFound = paths.length === 0;
        }

        li.innerHTML = `
                    <div class="query-color" style="background: ${q.color}"></div>
                    <div class="query-text ${isNotFound ? 'not-found' : ''}">${q.word} ${q.type === 'group' ? '<span style="font-size:0.8em; opacity:0.7;">(Group)</span>' : ''}</div>
                    <div class="query-visibility ${q.visible ? 'visible' : ''}" title="Toggle Visibility">
                        <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                            ${q.visible
                ? '<path d="M1 12s4-8 11-8 11 8 11 8-4 8-11 8-11-8-11-8z"></path><circle cx="12" cy="12" r="3"></circle>'
                : '<path d="M17.94 17.94A10.07 10.07 0 0 1 12 20c-7 0-11-8-11-8a18.45 18.45 0 0 1 5.06-5.94M9.9 4.24A9.12 9.12 0 0 1 12 4c7 0 11 8 11 8a18.5 18.5 0 0 1-2.16 3.19m-6.72-1.07a3 3 0 1 1-4.24-4.24"></path><line x1="1" y1="1" x2="23" y2="23"></line>'}
                        </svg>
                    </div>
                    <div class="query-delete" title="Delete Word">
                        <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                            <polyline points="3 6 5 6 21 6"></polyline><path d="M19 6v14a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2V6m3 0V4a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2"></path>
                        </svg>
                    </div>
                `;

        // Add event listeners (split into two because of toggle)
        const textEl = li.querySelector('.query-text');
        const colorEl = li.querySelector('.query-color');
        const visibilityEl = li.querySelector('.query-visibility');
        const deleteEl = li.querySelector('.query-delete');

        // Click text to reload word into search input
        const loadQuery = () => {
            if (q.type === 'group') {
                searchInput.value = q.word;
                colorPicker.value = q.color;
                window.selectedCells = [...q.cells];
                drawPaths();
            } else {
                window.selectedCells = [];
                searchInput.value = q.word;
                colorPicker.value = q.color;
                handleSearch();
            }
        };

        textEl.addEventListener('click', loadQuery);
        colorEl.addEventListener('click', loadQuery);

        visibilityEl.addEventListener('click', (e) => {
            e.stopPropagation();
            q.visible = !q.visible;
            localStorage.setItem('letterGridQueries', JSON.stringify(savedQueries));
            renderSavedQueries();
            drawPaths();
        });

        deleteEl.addEventListener('click', (e) => {
            e.stopPropagation();
            savedQueries.splice(index, 1);
            localStorage.setItem('letterGridQueries', JSON.stringify(savedQueries));
            if (searchInput.value.toUpperCase() === q.word) {
                searchInput.value = '';
                currentPaths = [];
            }
            renderSavedQueries();
            drawPaths();
        });

        // Drag and drop logic
        li.draggable = true;
        li.dataset.index = index;

        li.addEventListener('dragstart', (e) => {
            e.dataTransfer.effectAllowed = 'move';
            e.dataTransfer.setData('text/plain', index);
            li.classList.add('dragging');
        });

        li.addEventListener('dragover', (e) => {
            e.preventDefault();
            e.dataTransfer.dropEffect = 'move';
            li.classList.add('drag-over');
        });

        li.addEventListener('dragleave', () => {
            li.classList.remove('drag-over');
        });

        li.addEventListener('drop', (e) => {
            e.preventDefault();
            e.stopPropagation();
            li.classList.remove('drag-over');
            const dragIndex = parseInt(e.dataTransfer.getData('text/plain'), 10);
            const dropIndex = parseInt(li.dataset.index, 10);

            if (dragIndex !== dropIndex && !isNaN(dragIndex) && !isNaN(dropIndex)) {
                const draggedItem = savedQueries[dragIndex];
                savedQueries.splice(dragIndex, 1);
                savedQueries.splice(dropIndex, 0, draggedItem);

                localStorage.setItem('letterGridQueries', JSON.stringify(savedQueries));
                renderSavedQueries();
                drawPaths();
            }
        });

        li.addEventListener('dragend', () => {
            li.classList.remove('dragging');
            savedQueriesList.querySelectorAll('.saved-query').forEach(item => item.classList.remove('drag-over'));
        });

        savedQueriesList.appendChild(li);
    });
}

btnSave.addEventListener('click', () => {
    if (window.selectedCells && window.selectedCells.length > 0) {
        let groupName = searchInput.value.trim().toUpperCase();
        const existingGroupIndex = savedQueries.findIndex(q => q.word === groupName && q.type === 'group');

        if (existingGroupIndex === -1 || !groupName) {
            const promptName = prompt("Enter a name for this cell group:", groupName || "My Group");
            if (!promptName) return;
            groupName = promptName.trim().toUpperCase();
        }

        const existingIndex = savedQueries.findIndex(q => q.word === groupName);
        if (existingIndex > -1) {
            savedQueries[existingIndex] = {
                type: 'group',
                word: groupName,
                cells: [...window.selectedCells],
                color: colorPicker.value,
                visible: true
            };
        } else {
            savedQueries.push({
                type: 'group',
                word: groupName,
                cells: [...window.selectedCells],
                color: colorPicker.value,
                visible: true
            });
        }

        window.selectedCells = [];
        searchInput.value = '';
        handleSearch();
        localStorage.setItem('letterGridQueries', JSON.stringify(savedQueries));
        renderSavedQueries();
        return;
    }

    const word = searchInput.value.trim().toUpperCase();
    if (!word) return;

    // Check if already exists
    const existingIndex = savedQueries.findIndex(q => q.word === word);
    if (existingIndex > -1) {
        savedQueries[existingIndex].color = colorPicker.value;
    } else {
        savedQueries.push({
            word: word,
            color: colorPicker.value,
            visible: true
        });
    }

    localStorage.setItem('letterGridQueries', JSON.stringify(savedQueries));
    renderSavedQueries();
});

// Initialize UI
renderSavedQueries();

const btnExport = document.getElementById('btnExport');
const btnImport = document.getElementById('btnImport');

btnExport.addEventListener('click', async () => {
    const dataStr = JSON.stringify(savedQueries);
    try {
        await navigator.clipboard.writeText(dataStr);
        alert('Copied to clipboard!');
    } catch (err) {
        prompt('Copy this text:', dataStr);
    }
});

btnImport.addEventListener('click', () => {
    const dataStr = prompt('Paste your word list JSON:');
    if (!dataStr) return;
    try {
        const imported = JSON.parse(dataStr);
        if (Array.isArray(imported)) {
            imported.forEach(impQ => {
                const existingIndex = savedQueries.findIndex(q => q.word === impQ.word);
                if (existingIndex > -1) {
                    savedQueries[existingIndex] = impQ;
                } else {
                    savedQueries.push(impQ);
                }
            });
            localStorage.setItem('letterGridQueries', JSON.stringify(savedQueries));
            renderSavedQueries();
            drawPaths();
        }
    } catch (err) {
        alert('Invalid JSON data. Paste exactly what was exported.');
    }
});

async function loadState(name) {
    if (name === 'empty') {
        if (confirm('Clear all saved words and groups?')) {
            savedQueries = [];
            localStorage.setItem('letterGridQueries', JSON.stringify(savedQueries));
            renderSavedQueries();
            drawPaths();
        }
        return;
    }

    try {
        const response = await fetch(`/templates/jsons/${name}.json`);
        if (!response.ok) throw new Error('Failed to fetch state');
        const data = await response.json();
        if (Array.isArray(data)) {
            savedQueries = data;
            localStorage.setItem('letterGridQueries', JSON.stringify(savedQueries));
            renderSavedQueries();
            drawPaths();
        }
    } catch (err) {
        console.error(err);
        alert('Error loading state file. Make sure /static/jsons/' + name + '.json exists.');
    }
}

// Default to State 3 if no queries exist
if (savedQueries.length === 0 && !localStorage.getItem('letterGridInitialized')) {
    localStorage.setItem('letterGridInitialized', 'true');
    loadState('state3');
}\n
async function init() {
    try {
        const wRes = await fetch('../words.txt');
        const wText = await wRes.text();
        wordsList = wText.split('\n').map(w => w.trim().toUpperCase()).filter(w => w);
        
        const lRes = await fetch('../letters.txt');
        const lText = await lRes.text();
        const lLines = lText.split('\n').map(l => l.trim().toUpperCase()).filter(l => l);
        
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
\ninit();\n