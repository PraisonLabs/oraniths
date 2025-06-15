import React from 'react';

const App: React.FC = () => {
  return (
    <div className="app">
      <header>
        <h1>Oraniths</h1>
        <p>Natural Language Knowledge Graph Explorer</p>
      </header>
      <main>
        <div className="placeholder">
          <p>Graph visualization coming soon...</p>
        </div>
      </main>
    </div>
  );
};

export default App;
import React, { useState } from 'react';
import GraphVisualization from './components/GraphVisualization';
import { Graph } from '../common/types';
  const [query, setQuery] = useState('');
  const [graph, setGraph] = useState<Graph>({
    nodes: [
      { id: '1', label: 'React', type: 'concept' },
      { id: '2', label: 'TypeScript', type: 'concept' }
    ],
    edges: [{ id: 'e1', source: '1', target: '2', label: 'uses' }]
  });

    <div style={{ padding: '20px' }}>
      <header style={{ textAlign: 'center', marginBottom: '30px' }}>
        <h1 style={{ color: '#ff6b35' }}>🧠 Oraniths</h1>
        <form style={{ marginBottom: '20px' }}>
          <input type="text" value={query} onChange={(e) => setQuery(e.target.value)} 
                 placeholder="Enter your query..." style={{ width: '70%', padding: '10px' }} />
          <button type="submit" style={{ padding: '10px 20px', backgroundColor: '#ff6b35', color: 'white', border: 'none' }}>
            Explore
          </button>
        </form>
        <GraphVisualization graph={graph} />
export default App;
const handleQuerySubmit = async (e: React.FormEvent) => {    e.preventDefault();    if (!query.trim()) return;    try {      const response = await fetch("/api/query", {        method: "POST", headers: { "Content-Type": "application/json" },        body: JSON.stringify({ query })      });      const result = await response.json();      setGraph(result.graph);    } catch (error) { console.error("Failed to fetch graph:", error); }  };
        <form onSubmit={handleQuerySubmit} style={{ marginBottom: '20px' }}>