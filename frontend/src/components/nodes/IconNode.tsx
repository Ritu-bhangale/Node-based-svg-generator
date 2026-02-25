import { KeyboardEvent, useEffect, useState } from "react";
import { Handle, NodeProps, Position } from "reactflow";

import { CanvasNodeData } from "@/lib/types";

export function IconNode({ data }: NodeProps<CanvasNodeData>) {
  const [prompt, setPrompt] = useState("");
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState("");

  useEffect(() => {
    if (!data.isActive) {
      setPrompt("");
      setSubmitting(false);
      setError("");
    }
  }, [data.isActive]);

  const submit = async () => {
    const trimmed = prompt.trim();
    if (!trimmed || submitting) return;

    setError("");
    setSubmitting(true);
    try {
      await data.onCompleteMutation(data.nodeId, trimmed);
      setPrompt("");
      setError("");
    } catch (err) {
      const message = err instanceof Error ? err.message : "Mutation failed. Try a clearer prompt.";
      setError(message);
      setSubmitting(false);
    }
  };

  const onKeyDown = (event: KeyboardEvent<HTMLInputElement>) => {
    if (event.key === "Enter") {
      event.preventDefault();
      void submit();
    }
    if (event.key === "Escape") {
      event.preventDefault();
      setError("");
      data.onCancelMutation();
    }
  };

  return (
    <div style={{ position: "relative" }} className="icon-node-wrap">
      <div
        style={{
          background: "#FFFFFF",
          border: "1px solid #E5E7EB",
          borderRadius: 14,
          width: 240,
          padding: 16,
        }}
      >
        <div style={{ fontSize: 12, color: "#6B7280", marginBottom: 10 }}>{data.userInput ? "Mutated" : "Source"}</div>
        {data.isLoading ? (
          <div
            style={{
              width: 120,
              height: 120,
              margin: "0 auto",
              display: "flex",
              flexDirection: "column",
              alignItems: "center",
              justifyContent: "center",
              gap: 8,
              color: "#6B7280",
              fontSize: 12,
            }}
          >
            <div className="node-spinner" />
            <span>Processing...</span>
          </div>
        ) : (
          <div
            style={{
              width: 100,
              height: 100,
              margin: "0 auto",
              display: "flex",
              alignItems: "center",
              justifyContent: "center",
            }}
            dangerouslySetInnerHTML={{ __html: data.svg }}
          />
        )}
      </div>

      <button
        type="button"
        aria-label="Add mutation"
        onClick={() => data.onStartMutation(data.nodeId)}
        className="node-plus-btn"
        disabled={Boolean(data.isLoading)}
        style={{
          position: "absolute",
          right: -14,
          top: "50%",
          transform: "translateY(-50%)",
          width: 28,
          height: 28,
          borderRadius: 999,
          border: "1px solid #D1D5DB",
          background: "#FFFFFF",
          color: "#111827",
          fontSize: 18,
          lineHeight: "26px",
          textAlign: "center",
          padding: 0,
          cursor: "pointer",
          opacity: 1,
          transition: "border-color 120ms ease, background-color 120ms ease",
        }}
      >
        +
      </button>

      {data.isActive ? (
        <div
          style={{
            position: "absolute",
            left: "calc(100% + 24px)",
            top: "50%",
            transform: "translateY(-50%)",
            width: 260,
            border: "1px solid #E5E7EB",
            borderRadius: 10,
            padding: 12,
            background: "#FFFFFF",
            zIndex: 8,
          }}
        >
          <input
            autoFocus
            value={prompt}
            onChange={(e) => {
              setPrompt(e.target.value);
              if (error) setError("");
            }}
            onKeyDown={onKeyDown}
            placeholder="Describe the change..."
            style={{
              width: "100%",
              border: "1px solid #E5E7EB",
              borderRadius: 8,
              padding: "8px 10px",
              fontSize: 14,
              outline: "none",
            }}
          />
          {error ? <p style={{ margin: "8px 0 0", color: "#B91C1C", fontSize: 12 }}>{error}</p> : null}
        </div>
      ) : null}

      <Handle type="target" position={Position.Left} style={{ opacity: 0 }} />
      <Handle type="source" position={Position.Right} style={{ opacity: 0 }} />
    </div>
  );
}
