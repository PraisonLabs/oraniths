// Core type definitions for Oraniths

export interface Node {
  id: string;
  label: string;
  type: 'concept' | 'entity' | 'relationship';
  weight?: number;
}

export interface Edge {
  id: string;
  source: string;
  target: string;
  label?: string;
  weight?: number;
}

export interface Graph {
  nodes: Node[];
  edges: Edge[];
}

export interface QueryResult {
  query: string;
  graph: Graph;
  timestamp: number;
}