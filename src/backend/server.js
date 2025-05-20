
const express = require('express');
const cors = require('cors');

const app = express();
const PORT = process.env.PORT || 3001;

app.use(cors());
app.use(express.json());

app.get('/api/health', (req, res) => {
  res.json({ status: 'ok', timestamp: new Date().toISOString() });
});

app.post('/api/query', (req, res) => {
  const { query } = req.body;
  res.json({
    query,
    graph: { nodes: [{ id: '1', label: 'Sample Node', type: 'concept' }], edges: [] },
    timestamp: Date.now()
  });
});

app.listen(PORT, () => {
  console.log(`Server running on port ${PORT}`);
});
  const graph = generateGraphFromQuery(query);
  res.json({ query, graph, timestamp: Date.now() });
function generateGraphFromQuery(query) {
  const keywords = query.toLowerCase().split(/\s+/);
  const nodes = [], edges = [];
  const techRelations = {
    'react': ['javascript', 'jsx', 'components'],
    'nodejs': ['javascript', 'backend', 'server'],
    'typescript': ['javascript', 'types', 'compiler']
  };
  
  let nodeId = 1;
  const nodeMap = new Map();
  
  keywords.forEach(keyword => {
    if (techRelations[keyword]) {
      if (\!nodeMap.has(keyword)) {
        nodes.push({ id: nodeId.toString(), label: keyword, type: 'concept' });
        nodeMap.set(keyword, nodeId.toString());
        nodeId++;
      }
      
      techRelations[keyword].forEach(related => {
        if (\!nodeMap.has(related)) {
          nodes.push({ id: nodeId.toString(), label: related, type: 'entity' });
          nodeMap.set(related, nodeId.toString());
          nodeId++;
        }
        edges.push({ id: `e${edges.length + 1}`, source: nodeMap.get(keyword), target: nodeMap.get(related), label: 'relates to' });
      });
    }
  });
  
  if (nodes.length === 0) nodes.push({ id: '1', label: 'Unknown Topic', type: 'concept' });
  return { nodes, edges };
}

app.listen(PORT, () => console.log(`Server running on port ${PORT}`));