const dirs = [
  [-1, -1], [-1, 0], [-1, 1],
  [0, -1],          [0, 1],
  [1, -1],  [1, 0], [1, 1]
];

export function checkEquivalent(gridLetter, searchLetter, equivalenciesStr) {
  if (gridLetter === searchLetter) return true;
  const eqStr = equivalenciesStr.trim().toUpperCase();
  if (!eqStr) return false;

  const groups = eqStr.split(',').map(s => s.split('=').map(c => c.trim()).filter(c => c));
  for (let g of groups) {
      if (g.includes(gridLetter) && g.includes(searchLetter)) {
          return true;
      }
  }
  return false;
}

export function findPaths(word, gridData, options) {
  if (!word || !gridData || gridData.length === 0) return [];
  const rows = gridData.length;
  const cols = gridData[0].length;
  const w = word.toUpperCase();
  let allPaths = [];

  const { reuse, straight, equivalencies } = options;

  function dfs(r, c, index, path, visited, direction) {
      if (index === w.length) {
          allPaths.push([...path]);
          return true;
      }
      let foundAny = false;
      for (let d of dirs) {
          if (straight && direction !== null && (direction[0] !== d[0] || direction[1] !== d[1])) {
              continue;
          }

          let nr = r + d[0], nc = c + d[1];
          if (nr >= 0 && nr < rows && nc >= 0 && nc < cols) {
              const canVisit = reuse ? true : !visited[nr][nc];
              if (canVisit && checkEquivalent(gridData[nr][nc], w[index], equivalencies)) {
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
          if (checkEquivalent(gridData[r][c], w[0], equivalencies)) {
              let visited = Array.from({ length: rows }, () => Array(cols).fill(false));
              visited[r][c] = true;
              dfs(r, c, 1, [[r, c]], visited, null);
          }
      }
  }
  return allPaths;
}

export async function buildWordMap(gridData, wordsList, options) {
  if (!gridData || gridData.length === 0) return { tileWordsMap: {}, allWords: [] };
  const rows = gridData.length;
  const cols = gridData[0].length;
  
  let tileWordsMap = {};
  for (let r = 0; r < rows; r++) {
      for (let c = 0; c < cols; c++) {
          tileWordsMap[`${r},${c}`] = new Set();
      }
  }
  
  const { reuse, straight, equivalencies } = options;
  
  function dfs(r, c, remaining, seen, word, direction) {
      for (let d of dirs) {
          if (straight && direction !== null && (direction[0] !== d[0] || direction[1] !== d[1])) continue;
          let nr = r + d[0];
          let nc = c + d[1];
          if (nr >= 0 && nr < rows && nc >= 0 && nc < cols) {
              if (!reuse && seen.some(pos => pos[0] === nr && pos[1] === nc)) continue;
              
              if (checkEquivalent(gridData[nr][nc], remaining[0], equivalencies)) {
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
                      if (checkEquivalent(gridData[r][c], word[0], equivalencies)) {
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
              // Convert Sets to Arrays and sort
              const finalMap = {};
              for (let key in tileWordsMap) {
                finalMap[key] = Array.from(tileWordsMap[key]).sort();
              }
              const allWords = Array.from(uniqueWords).sort((a, b) => b.length - a.length);
              resolve({ tileWordsMap: finalMap, allWords });
          }
      }
      processChunk();
  });
}
