"use client";

import { ChangeEvent, useMemo, useState } from "react";
import ReactFlow, { Background, NodeTypes, applyEdgeChanges, applyNodeChanges } from "reactflow";

import { IconNode } from "@/components/nodes/IconNode";
import { generateIcons } from "@/lib/api";
import { CanvasNodeData } from "@/lib/types";
import { useGraphStore } from "@/store/graphStore";

export default function HomePage() {
  const nodes = useGraphStore((s) => s.nodes);
  const edges = useGraphStore((s) => s.edges);
  const activeNodeId = useGraphStore((s) => s.activeNodeId);
  const setNodes = useGraphStore((s) => s.setNodes);
  const setEdges = useGraphStore((s) => s.setEdges);
  const onConnect = useGraphStore((s) => s.onConnect);
  const addRootNode = useGraphStore((s) => s.addRootNode);
  const startMutation = useGraphStore((s) => s.startMutation);
  const cancelMutation = useGraphStore((s) => s.cancelMutation);
  const completeMutation = useGraphStore((s) => s.completeMutation);

  const [prompt, setPrompt] = useState("");
  const [uploadedSvg, setUploadedSvg] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  const nodeTypes: NodeTypes = useMemo(() => ({ IconNode }), []);

  const mappedNodes = useMemo(
    () =>
      nodes.map((node) => ({
        ...node,
        data: {
          ...(node.data as CanvasNodeData),
          isActive: activeNodeId === node.id,
          onStartMutation: startMutation,
          onCancelMutation: cancelMutation,
          onCompleteMutation: completeMutation,
        },
      })),
    [nodes, activeNodeId, startMutation, cancelMutation, completeMutation]
  );

  const onUpload = async (event: ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0];
    if (!file) return;
    const content = await file.text();
    setUploadedSvg(content.trim());
  };

  const onGenerate = async () => {
    setError("");

    if (uploadedSvg && !prompt.trim()) {
      addRootNode(uploadedSvg);
      return;
    }

    if (!prompt.trim()) {
      setError("Describe the icon to continue.");
      return;
    }

    setLoading(true);
    try {
      const variants = await generateIcons({
        prompt: prompt.trim(),
        brandConstraints: {
          grid: 24,
          strokeWidth: 2,
          style: "outline",
        },
      });

      if (!variants.length) {
        throw new Error("No SVG variants returned");
      }

      addRootNode(variants[0]);
    } catch (e) {
      setError(e instanceof Error ? e.message : "Generate failed");
    } finally {
      setLoading(false);
    }
  };

  return (
    <main style={{ height: "100vh", width: "100vw", position: "relative" }}>
      <ReactFlow
        style={{ width: "100%", height: "100%" }}
        nodes={mappedNodes}
        edges={edges}
        nodeTypes={nodeTypes}
        fitView
        onNodesChange={(changes) => setNodes((current) => applyNodeChanges(changes, current))}
        onEdgesChange={(changes) => setEdges((current) => applyEdgeChanges(changes, current))}
        onConnect={onConnect}
      >
        <Background gap={22} size={1} color="#E5E7EB" />
      </ReactFlow>

      {nodes.length === 0 ? (
        <div
          style={{
            position: "absolute",
            inset: 0,
            display: "flex",
            alignItems: "center",
            justifyContent: "center",
            pointerEvents: "none",
          }}
        >
          <div
            style={{
              width: 420,
              background: "#FFFFFF",
              border: "1px solid #E5E7EB",
              borderRadius: 12,
              padding: 24,
              pointerEvents: "auto",
            }}
          >
            <h1 style={{ margin: 0, fontSize: 18, fontWeight: 600 }}>Create Icon</h1>
            <input
              value={prompt}
              onChange={(e) => setPrompt(e.target.value)}
              placeholder="Describe the icon..."
              style={{
                width: "100%",
                marginTop: 14,
                border: "1px solid #E5E7EB",
                borderRadius: 10,
                padding: "10px 12px",
                fontSize: 14,
                outline: "none",
              }}
            />

            <div style={{ display: "flex", gap: 10, marginTop: 12 }}>
              <label
                htmlFor="svg-upload"
                style={{
                  display: "inline-flex",
                  alignItems: "center",
                  border: "1px solid #E5E7EB",
                  borderRadius: 8,
                  padding: "8px 10px",
                  fontSize: 12,
                  color: "#374151",
                  cursor: "pointer",
                }}
              >
                Upload SVG
              </label>
              <input id="svg-upload" type="file" accept=".svg,image/svg+xml" onChange={onUpload} style={{ display: "none" }} />
              {uploadedSvg ? <span style={{ fontSize: 12, color: "#6B7280", alignSelf: "center" }}>SVG ready</span> : null}
            </div>

            <button
              type="button"
              onClick={onGenerate}
              disabled={loading}
              style={{
                marginTop: 14,
                width: "100%",
                border: "1px solid #111827",
                borderRadius: 10,
                padding: "10px 12px",
                background: "#111827",
                color: "#FFFFFF",
                fontSize: 14,
                cursor: "pointer",
              }}
            >
              {loading ? "Generating..." : "Generate"}
            </button>

            {error ? <p style={{ margin: "10px 0 0", color: "#B91C1C", fontSize: 13 }}>{error}</p> : null}
          </div>
        </div>
      ) : null}
    </main>
  );
}
