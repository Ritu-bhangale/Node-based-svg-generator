import { create } from "zustand";
import { addEdge, Connection, Edge, Node } from "reactflow";

import { mutateSvg } from "@/lib/api";
import { CanvasNodeData, SvgGraphRecord } from "@/lib/types";

interface GraphState {
  nodes: Node<CanvasNodeData>[];
  edges: Edge[];
  records: Record<string, SvgGraphRecord>;
  activeNodeId: string | null;
  setNodes: (updater: (nodes: Node<CanvasNodeData>[]) => Node<CanvasNodeData>[]) => void;
  setEdges: (updater: (edges: Edge[]) => Edge[]) => void;
  onConnect: (connection: Connection) => void;
  addRootNode: (svg: string) => string;
  startMutation: (nodeId: string) => void;
  cancelMutation: () => void;
  completeMutation: (nodeId: string, prompt: string) => Promise<void>;
}

function makeId(prefix: string): string {
  return `${prefix}-${Date.now()}-${Math.random().toString(36).slice(2, 8)}`;
}

export const useGraphStore = create<GraphState>((set, get) => ({
  nodes: [],
  edges: [],
  records: {},
  activeNodeId: null,

  setNodes: (updater) => set((state) => ({ nodes: updater(state.nodes) })),
  setEdges: (updater) => set((state) => ({ edges: updater(state.edges) })),
  onConnect: (connection) => set((state) => ({ edges: addEdge(connection, state.edges) })),

  addRootNode: (svg) => {
    const id = makeId("node");
    const node: Node<CanvasNodeData> = {
      id,
      type: "IconNode",
      position: { x: 120, y: 140 },
      data: {
        label: "Generated",
        svg,
        nodeId: id,
        isActive: false,
        onStartMutation: () => {},
        onCancelMutation: () => {},
        onCompleteMutation: async () => {},
      },
    };

    const record: SvgGraphRecord = {
      id,
      parentId: null,
      svgSnapshot: svg,
      createdAt: Date.now(),
    };

    set((state) => ({
      nodes: [...state.nodes, node],
      records: { ...state.records, [id]: record },
      activeNodeId: null,
    }));

    return id;
  },

  startMutation: (nodeId) => set(() => ({ activeNodeId: nodeId })),
  cancelMutation: () => set(() => ({ activeNodeId: null })),

  completeMutation: async (nodeId, prompt) => {
    const state = get();
    const parentRecord = state.records[nodeId];
    const parentNode = state.nodes.find((n) => n.id === nodeId);
    if (!parentRecord || !parentNode) {
      throw new Error("Parent node not found");
    }

    const childId = makeId("node");
    const childEdgeId = `${nodeId}-${childId}`;
    const childNode: Node<CanvasNodeData> = {
      id: childId,
      type: "IconNode",
      position: {
        x: parentNode.position.x + 300,
        y: parentNode.position.y,
      },
      data: {
        label: "Generating...",
        svg: "",
        userInput: prompt,
        isLoading: true,
        nodeId: childId,
        isActive: false,
        onStartMutation: () => {},
        onCancelMutation: () => {},
        onCompleteMutation: async () => {},
      },
    };

    set((curr) => ({
      nodes: [...curr.nodes, childNode],
      edges: [...curr.edges, { id: childEdgeId, source: nodeId, target: childId }],
      activeNodeId: null,
    }));

    try {
      const mutatedSvg = await mutateSvg({
        svg: parentRecord.svgSnapshot,
        userInput: prompt,
      });

      const childRecord: SvgGraphRecord = {
        id: childId,
        parentId: nodeId,
        svgSnapshot: mutatedSvg,
        userInput: prompt,
        createdAt: Date.now(),
      };

      set((curr) => ({
        nodes: curr.nodes.map((n) =>
          n.id === childId
            ? {
                ...n,
                data: {
                  ...n.data,
                  label: "Mutation",
                  svg: mutatedSvg,
                  isLoading: false,
                },
              }
            : n
        ),
        records: { ...curr.records, [childId]: childRecord },
      }));
    } catch (error) {
      set((curr) => ({
        nodes: curr.nodes.filter((n) => n.id !== childId),
        edges: curr.edges.filter((e) => e.id !== childEdgeId),
      }));
      throw error;
    }
  },
}));
