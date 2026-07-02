import { useState, useEffect, useCallback } from 'react';
import LetterGrid from './components/LetterGrid';
import Sidebar from './components/Sidebar';
import { buildWordMap, findPaths } from './utils/solver';

function App() {
  const [gridData, setGridData] = useState([]);
  const [wordsList, setWordsList] = useState([]);
  const [allWords, setAllWords] = useState([]);
  const [tileWordsMap, setTileWordsMap] = useState({});
  const [isComputing, setIsComputing] = useState(false);
  const [loadingMsg, setLoadingMsg] = useState('Initializing...');

  const [savedQueries, setSavedQueries] = useState(() => {
    return JSON.parse(localStorage.getItem('letterGridQueries') || '[]');
  });

  const [settings, setSettings] = useState({
    reuse: localStorage.getItem('letterGridReuse') === 'true',
    straight: localStorage.getItem('letterGridStraight') === 'true',
    showLines: localStorage.getItem('letterGridShowLines') !== 'false',
    equivalencies: localStorage.getItem('letterGridEquiv') || ''
  });

  const [searchQuery, setSearchQuery] = useState('');
  const [color, setColor] = useState('#ef4444');
  const [selectedCells, setSelectedCells] = useState([]);
  const [hoverWord, setHoverWord] = useState(null);

  useEffect(() => {
    localStorage.setItem('letterGridQueries', JSON.stringify(savedQueries));
  }, [savedQueries]);

  useEffect(() => {
    localStorage.setItem('letterGridReuse', settings.reuse);
    localStorage.setItem('letterGridStraight', settings.straight);
    localStorage.setItem('letterGridShowLines', settings.showLines);
    localStorage.setItem('letterGridEquiv', settings.equivalencies);
  }, [settings]);

  const loadData = async () => {
    setIsComputing(true);
    setLoadingMsg('Loading static files...');
    try {
      const [wRes, lRes] = await Promise.all([
        fetch('/words.txt'),
        fetch('/letters.txt')
      ]);
      const wText = await wRes.text();
      const lText = await lRes.text();

      const words = wText.split('\n').map(w => w.trim().toUpperCase()).filter(w => w);
      const lines = lText.split('\n').map(l => l.trim().toUpperCase()).filter(l => l);
      
      const grid = lines.map(l => l.split(''));
      // if short, pad it
      while (grid.length < 14) grid.push(Array(14).fill('?'));

      setWordsList(words);
      setGridData(grid);

      setLoadingMsg('Computing paths...');
      const { tileWordsMap: newMap, allWords: newAll } = await buildWordMap(grid, words, settings);
      setTileWordsMap(newMap);
      setAllWords(newAll);
    } catch (err) {
      console.error(err);
    } finally {
      setIsComputing(false);
    }
  };

  useEffect(() => {
    loadData();
  }, []); // on mount

  const handleRecompute = async () => {
    setIsComputing(true);
    setLoadingMsg('Recomputing paths...');
    // slight delay for UI update
    await new Promise(r => setTimeout(r, 50));
    const { tileWordsMap: newMap, allWords: newAll } = await buildWordMap(gridData, wordsList, settings);
    setTileWordsMap(newMap);
    setAllWords(newAll);
    setIsComputing(false);
  };

  const currentPaths = findPaths(hoverWord || searchQuery, gridData, settings);

  const updateSetting = (key, val) => {
    setSettings(s => ({ ...s, [key]: val }));
  };

  const handleSave = () => {
    if (selectedCells.length > 0) {
      let groupName = searchQuery.trim().toUpperCase();
      if (!groupName) {
        const promptName = prompt("Enter a name for this cell group:", "My Group");
        if (!promptName) return;
        groupName = promptName.trim().toUpperCase();
      }
      const existingIdx = savedQueries.findIndex(q => q.word === groupName);
      const newGroup = { type: 'group', word: groupName, cells: [...selectedCells], color, visible: true };
      if (existingIdx > -1) {
        const copy = [...savedQueries];
        copy[existingIdx] = newGroup;
        setSavedQueries(copy);
      } else {
        setSavedQueries([...savedQueries, newGroup]);
      }
      setSelectedCells([]);
      setSearchQuery('');
    } else {
      const word = searchQuery.trim().toUpperCase();
      if (!word) return;
      const existingIdx = savedQueries.findIndex(q => q.word === word);
      if (existingIdx > -1) {
        const copy = [...savedQueries];
        copy[existingIdx].color = color;
        setSavedQueries(copy);
      } else {
        setSavedQueries([...savedQueries, { word, color, visible: true }]);
      }
    }
  };

  return (
    <div className="w-full min-h-screen">
      <header className="w-full py-8 text-center">
        <h1 className="m-0 text-4xl font-extrabold tracking-widest text-transparent bg-clip-text bg-gradient-to-r from-sky-400 to-indigo-400">LetterGrid</h1>
      </header>

      <div className="flex flex-col lg:flex-row gap-12 w-11/12 mx-auto mb-12 items-start justify-center">
        <div className="flex flex-col gap-6 flex-none">
          <div className="flex gap-4 items-center bg-slate-800/70 p-4 rounded-2xl backdrop-blur-md border border-white/10 shadow-2xl">
            <input 
              type="text" 
              value={searchQuery}
              onChange={e => setSearchQuery(e.target.value.toUpperCase())}
              placeholder="Type a word..." 
              className="flex-grow p-3 rounded-lg border border-white/20 bg-slate-900/60 text-white text-xl font-semibold outline-none transition focus:border-sky-400 uppercase"
            />
            <input 
              type="color" 
              value={color}
              onChange={e => setColor(e.target.value)}
              className="w-10 h-10 border-none rounded-full cursor-pointer bg-transparent"
            />
            <button onClick={handleSave} className="py-3 px-6 bg-blue-500 hover:bg-blue-600 active:scale-95 text-white border-none rounded-lg font-semibold text-base cursor-pointer transition">
              Save
            </button>
          </div>

          <LetterGrid 
            gridData={gridData}
            searchPaths={currentPaths}
            searchColor={color}
            savedQueries={savedQueries}
            settings={settings}
            selectedCells={selectedCells}
            setSelectedCells={setSelectedCells}
            tileWordsMap={tileWordsMap}
            setSearchQuery={setSearchQuery}
            setHoverWord={setHoverWord}
            findPaths={(w) => findPaths(w, gridData, settings)}
          />
        </div>

        <Sidebar 
          settings={settings}
          updateSetting={updateSetting}
          handleRecompute={handleRecompute}
          isComputing={isComputing}
          loadingMsg={loadingMsg}
          savedQueries={savedQueries}
          setSavedQueries={setSavedQueries}
          setSearchQuery={setSearchQuery}
          setColor={setColor}
          setSelectedCells={setSelectedCells}
        />
      </div>

      <div className="w-11/12 max-w-7xl mx-auto mb-8 bg-slate-800/70 border border-white/10 rounded-2xl p-6 shadow-xl">
        <h2 className="mt-0 text-2xl border-b border-white/10 pb-2 mb-4">
          All Found Words <span className="text-slate-400 text-lg font-normal">({allWords.length})</span>
        </h2>
        <div className="flex flex-wrap gap-2 max-h-[250px] overflow-y-auto pr-2">
          {allWords.map(word => (
            <div 
              key={word}
              onClick={() => setSearchQuery(word)}
              onMouseEnter={() => setHoverWord(word)}
              onMouseLeave={() => setHoverWord(null)}
              className="bg-slate-900/60 border border-white/20 px-3 py-1 rounded-full text-sm cursor-pointer transition-colors hover:bg-blue-500 hover:border-blue-600 text-slate-200"
            >
              {word}
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}

export default App;
