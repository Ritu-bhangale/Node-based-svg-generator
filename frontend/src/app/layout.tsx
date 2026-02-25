import "reactflow/dist/style.css";
import "./globals.css";

import type { Metadata } from "next";
import { ReactNode } from "react";

export const metadata: Metadata = {
  title: "Node-Based SVG Mutation Engine",
  description: "MVP canvas for deterministic SVG mutations",
};

export default function RootLayout({ children }: { children: ReactNode }) {
  return (
    <html lang="en">
      <body>{children}</body>
    </html>
  );
}
