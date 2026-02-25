const BASE_URL = process.env.NEXT_PUBLIC_ENGINE_URL ?? "http://localhost:8000";

export interface MutatePayload {
  svg: string;
  userInput: string;
}

export interface GeneratePayload {
  prompt: string;
  brandConstraints: {
    grid: number;
    strokeWidth: number;
    style: "outline" | "filled";
  };
}

interface LlmDebugSection {
  request?: unknown;
  rawResponse?: unknown;
  parsed?: unknown;
  extracted?: unknown;
}

interface LlmDebugPayload {
  provider?: string;
  model?: string;
  planner?: LlmDebugSection;
  generator?: LlmDebugSection;
  variants?: Array<{
    variantIndex: number;
    planner?: LlmDebugSection;
    generator?: LlmDebugSection;
    normalizedSvg?: string;
  }>;
  normalizedSvg?: string;
}

function clipValue(value: unknown): unknown {
  if (typeof value === "string") {
    return value.length > 300 ? `${value.slice(0, 300)}...` : value;
  }
  return value;
}

function logPipelineDebug(debug: LlmDebugPayload): void {
  console.groupCollapsed("🧠 LLM Pipeline Debug");
  console.log("Provider:", debug.provider ?? "unknown");
  console.log("Model:", debug.model ?? "unknown");

  if (debug.variants?.length) {
    for (const variant of debug.variants) {
      console.group(`Planner (Variant ${variant.variantIndex})`);
      console.log("Request:", clipValue(variant.planner?.request));
      console.log("Raw Response:", clipValue(variant.planner?.rawResponse));
      console.log("Parsed JSON:", clipValue(variant.planner?.parsed));
      console.groupEnd();

      console.group(`SVG Generator (Variant ${variant.variantIndex})`);
      console.log("Request:", clipValue(variant.generator?.request));
      console.log("Raw Response:", clipValue(variant.generator?.rawResponse));
      console.log("Extracted SVG:", clipValue(variant.generator?.extracted));
      console.groupEnd();
    }
  } else {
    console.group("Planner");
    console.log("Request:", clipValue(debug.planner?.request));
    console.log("Raw Response:", clipValue(debug.planner?.rawResponse));
    console.log("Parsed JSON:", clipValue(debug.planner?.parsed));
    console.groupEnd();

    console.group("SVG Generator");
    console.log("Request:", clipValue(debug.generator?.request));
    console.log("Raw Response:", clipValue(debug.generator?.rawResponse));
    console.log("Extracted SVG:", clipValue(debug.generator?.extracted));
    console.groupEnd();
  }

  console.groupEnd();
}

export async function mutateSvg(payload: MutatePayload): Promise<string> {
  console.time("LLM Pipeline");
  const response = await fetch(`${BASE_URL}/mutate`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload),
  });

  if (!response.ok) {
    const message = await response.text();
    console.timeEnd("LLM Pipeline");
    throw new Error(`Mutation failed: ${message}`);
  }

  const data = (await response.json()) as { svg: string; debug?: LlmDebugPayload };
  if (data.debug) {
    logPipelineDebug(data.debug);
  }
  console.timeEnd("LLM Pipeline");
  return data.svg;
}

export async function generateIcons(payload: GeneratePayload): Promise<string[]> {
  console.time("LLM Pipeline");
  const response = await fetch(`${BASE_URL}/generate`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload),
  });

  if (!response.ok) {
    const message = await response.text();
    console.timeEnd("LLM Pipeline");
    throw new Error(`Generate failed: ${message}`);
  }

  const data = (await response.json()) as { variants: Array<{ svg: string }>; debug?: LlmDebugPayload };
  if (data.debug) {
    logPipelineDebug(data.debug);
  }
  console.timeEnd("LLM Pipeline");
  return (data.variants ?? []).map((v) => v.svg).filter(Boolean);
}
