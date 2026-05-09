import { useState } from "react";
import ReactFlow, {
  Background,
  Controls,
  ReactFlowProvider,
} from "reactflow";
import "reactflow/dist/style.css";
import { toPng } from "html-to-image";

function Flow() {
  const [nodes, setNodes] = useState<any[]>([]);
  const [edges, setEdges] = useState<any[]>([]);
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [explanation, setExplanation] = useState("");

  const processFile = async (file: File) => {
    setSelectedFile(file);

    const formData = new FormData();
    formData.append("file", file);

    let api = "http://127.0.0.1:8000/upload";

    if (
      file.name.endsWith(".yaml") ||
      file.name.endsWith(".yml")
    ) {
      api = "http://127.0.0.1:8000/upload-k8s";
    }

    const res = await fetch(api, {
      method: "POST",
      body: formData,
    });

    const data = await res.json();

    setNodes(data.nodes);
    setEdges(data.edges);
  };

  const explainArchitecture = async () => {
    if (!selectedFile) return;

    const formData = new FormData();
    formData.append("file", selectedFile);

    const res = await fetch(
      "http://127.0.0.1:8000/explain",
      {
        method: "POST",
        body: formData,
      }
    );

    const data = await res.json();
    setExplanation(data.explanation);
  };

  const downloadImage = async () => {
    const element = document.getElementById("diagram");
    if (!element) return;

    const dataUrl = await toPng(element);

    const link = document.createElement("a");
    link.download = "architecture.png";
    link.href = dataUrl;
    link.click();
  };

  return (
    <div style={{ width: "100vw", height: "100vh" }}>
      <div
        style={{
          background: "#111827",
          color: "white",
          padding: 20,
          textAlign: "center",
        }}
      >
        <h1>Infra Visualizer</h1>
        <p>Upload Terraform or Kubernetes files</p>

        <input
          type="file"
          onChange={(e: any) =>
            processFile(e.target.files[0])
          }
        />

        <button
          onClick={downloadImage}
          style={{
            marginLeft: 10,
            padding: "10px 20px",
            background: "#2563eb",
            color: "white",
            border: "none",
            borderRadius: 8,
          }}
        >
          Download PNG
        </button>

        <button
          onClick={explainArchitecture}
          style={{
            marginLeft: 10,
            padding: "10px 20px",
            background: "#16a34a",
            color: "white",
            border: "none",
            borderRadius: 8,
          }}
        >
          Explain Architecture
        </button>

        {explanation && (
          <div
            style={{
              marginTop: 20,
              background: "#1f2937",
              padding: 15,
              borderRadius: 10,
            }}
          >
            <h3>Architecture Explanation</h3>
            <p>{explanation}</p>
          </div>
        )}
      </div>

      <div
        id="diagram"
        style={{
          width: "100%",
          height: "85%",
        }}
      >
        <ReactFlow nodes={nodes} edges={edges} fitView>
          <Background />
          <Controls />
        </ReactFlow>
      </div>
    </div>
  );
}

export default function App() {
  return (
    <ReactFlowProvider>
      <Flow />
    </ReactFlowProvider>
  );
}