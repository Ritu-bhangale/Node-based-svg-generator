export type CanvasNodeType = "IconNode";

export interface SvgGraphRecord {
  id: string;
  parentId: string | null;
  svgSnapshot: string;
  userInput?: string;
  createdAt: number;
}

export interface CanvasNodeData {
  label: string;
  svg: string;
  userInput?: string;
  isLoading?: boolean;
  nodeId: string;
  isActive: boolean;
  onStartMutation: (nodeId: string) => void;
  onCancelMutation: () => void;
  onCompleteMutation: (nodeId: string, prompt: string) => Promise<void>;
}
