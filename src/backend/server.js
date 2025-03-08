
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