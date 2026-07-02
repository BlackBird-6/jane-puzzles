import { useState, useMemo } from 'react';

export default function LetterGrid({ 
  gridData, 
  searchPaths, 
  searchColor, 
  savedQueries, 
  settings,
  selectedCells,
  setSelectedCells,
  tileWordsMap,
  setSearchQuery,
  setHoverWord,
  findPaths
}) {
  const [localHoverWord, setLocalHoverWord] = useState(null);

  const stuffToDraw = useMemo(() => {
    let stuff = [];
    if (searchPaths && searchPaths.length > 0) {
      stuff.push({ paths: searchPaths, color: searchColor });
    }

    savedQueries.forEach(q => {
      if (q.visible) {
        if (q.type === 'group') {
          stuff.push({ paths: [q.cells], color: q.color, noLines: true });
        } else {
          const qPaths = findPaths(q.word);
          if (qPaths.length > 0) {
            stuff.push({ paths: qPaths, color: q.color });
          }
        }
      }
    });

    if (selectedCells && selectedCells.length > 0) {
      stuff.push({ paths: [selectedCells], color: searchColor, noLines: true, isSelection: true });
    }

    return stuff;
  }, [searchPaths, searchColor, savedQueries, selectedCells, findPaths]);

  const rows = gridData.length;
  const cols = rows > 0 ? gridData[0].length : 0;

  // Compute active tiles and lines
  const tileStates = {}; // `${r},${c}` -> { active: bool, selected: bool, background: string }
  const linesToDraw = [];

  stuffToDraw.forEach(item => {
    item.paths.forEach((path, pathIdx) => {
      let dStr = '';
      path.forEach((pos, idx) => {
        const r = pos[0], c = pos[1];
        const key = `${r},${c}`;
        if (!tileStates[key]) tileStates[key] = { active: false, selected: false, background: '' };
        
        tileStates[key].active = true;
        if (item.isSelection) tileStates[key].selected = true;
        tileStates[key].background = item.color;

        // Calculate center for SVG path (100 / cols)%
        const wPct = 100 / cols;
        const hPct = 100 / rows;
        const x = (c * wPct) + (wPct / 2);
        const y = (r * hPct) + (hPct / 2);

        if (idx === 0) {
          dStr += `M ${x} ${y} `;
        } else {
          dStr += `L ${x} ${y} `;
        }
      });

      if (settings.showLines && !item.noLines && path.length > 1) {
        linesToDraw.push({ d: dStr, color: item.color, id: `path-${item.color}-${pathIdx}` });
      }
    });
  });

  const handleTileClick = (e, r, c) => {
    if (e.ctrlKey) {
      const idx = selectedCells.findIndex(pos => pos[0] === r && pos[1] === c);
      if (idx > -1) {
        const newSel = [...selectedCells];
        newSel.splice(idx, 1);
        setSelectedCells(newSel);
      } else {
        setSelectedCells([...selectedCells, [r, c]]);
      }
      return;
    }

    setSelectedCells([]);
  };

  const activeTileWords = useMemo(() => {
    if (selectedCells.length !== 1) return null;
    const r = selectedCells[0][0];
    const c = selectedCells[0][1];
    const key = `${r},${c}`;
    const words = tileWordsMap[key] || [];
    const letter = gridData[r][c];
    
    const startsWith = words.filter(w => w.startsWith(letter));
    const others = words.filter(w => !w.startsWith(letter));
    return { letter, r, c, words: [...startsWith, ...others] };
  }, [selectedCells, tileWordsMap, gridData]);

  return (
    <div className="flex gap-8 items-start">
      <div className="relative bg-slate-800/70 p-4 sm:p-8 rounded-3xl shadow-2xl border border-white/5 backdrop-blur-md inline-block">
        <div 
          className="grid gap-2 relative z-10" 
          style={{ gridTemplateColumns: `repeat(${cols}, 1fr)` }}
        >
          {gridData.map((row, r) => (
            row.map((letter, c) => {
              const key = `${r},${c}`;
              const state = tileStates[key] || {};
              return (
                <div 
                  key={key}
                  onClick={(e) => handleTileClick(e, r, c)}
                  className={`tile cursor-pointer ${state.active ? 'active' : ''} ${state.selected ? 'selected' : ''}`}
                  style={{ background: state.background || '' }}
                >
                  {letter}
                </div>
              );
            })
          ))}
        </div>
        
        <svg className="absolute top-4 left-4 sm:top-8 sm:left-8 w-[calc(100%-2rem)] h-[calc(100%-2rem)] sm:w-[calc(100%-4rem)] sm:h-[calc(100%-4rem)] pointer-events-none z-20">
          {linesToDraw.map((line, i) => (
            // use % coordinates for SVG scaling
            <path 
              key={i} 
              d={line.d.replace(/([\d.]+) ([\d.]+)/g, (match, x, y) => `${x}% ${y}%`)} 
              className="line-path" 
              stroke={line.color} 
            />
          ))}
        </svg>
      </div>

      {activeTileWords && (
        <div className="w-64 bg-slate-800/70 rounded-3xl p-6 shadow-2xl border border-white/10 backdrop-blur-md">
          <h2 className="mt-0 text-xl text-slate-200 border-b border-white/10 pb-2 mb-4">
            Words on {activeTileWords.letter} ({activeTileWords.r},{activeTileWords.c})
          </h2>
          <ul className="list-none p-0 m-0 max-h-[400px] overflow-y-auto flex flex-col gap-2">
            {activeTileWords.words.length === 0 ? (
              <li className="text-slate-400 italic">No words found</li>
            ) : (
              activeTileWords.words.map(w => (
                <li 
                  key={w}
                  onClick={() => setSearchQuery(w)}
                  onMouseEnter={() => setHoverWord(w)}
                  onMouseLeave={() => setHoverWord(null)}
                  className="bg-slate-900/40 p-2 rounded-lg cursor-pointer hover:bg-slate-700/80 transition font-semibold"
                >
                  {w}
                </li>
              ))
            )}
          </ul>
        </div>
      )}
    </div>
  );
}
