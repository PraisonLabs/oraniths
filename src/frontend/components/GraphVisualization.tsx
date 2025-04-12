
import React, { useEffect, useRef } from 'react';
import cytoscape from 'cytoscape';
import cola from 'cytoscape-cola';
import { Graph } from '../../common/types';

cytoscape.use(cola);

interface GraphVisualizationProps {
  graph: Graph;
}

const GraphVisualization: React.FC<GraphVisualizationProps> = ({ graph }) => {
  const containerRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (\!containerRef.current) return;
    const cy = cytoscape({
      container: containerRef.current,
      elements: [
        ...graph.nodes.map(n => ({ data: { id: n.id, label: n.label, type: n.type } })),
        ...graph.edges.map(e => ({ data: { id: e.id, source: e.source, target: e.target, label: e.label } }))
      ],
      style: [
        { selector: 'node', style: { 'background-color': '#ff6b35', 'label': 'data(label)', 'color': '#fff' } },
        { selector: 'edge', style: { 'line-color': '#ccc', 'target-arrow-shape': 'triangle' } }
      ],
      layout: { name: 'cola', animate: true }
    });
    return () => cy.destroy();
  }, [graph]);

  return <div ref={containerRef} style={{ width: '100%', height: '500px', border: '1px solid #ddd' }} />;
};

export default GraphVisualization;