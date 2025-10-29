// import { useState, useRef } from "react";
// import api from "../api/client";
// import GlassHeader from "../components/GlassHeader";
// import BackgroundParticles from "../components/BackgroundParticles";
// import AgentOutputCard from "../components/AgentOutputCard";
// import AgentMetricsChart from "../components/AgentMetricsChart";

// export default function Home() {
//   const [outputs, setOutputs] = useState([]);
//   const [project, setProject] = useState(null);
//   const [loading, setLoading] = useState(false);
//   const [metrics, setMetrics] = useState({});
//   const scrollRef = useRef(null);

//   const runWorkflow = async () => {
//     setLoading(true);
//     try {
//       const res = await api.post("/agents/run", {
//         title: "AI Notes App",
//         prompt: "Build an AI-powered notes app with sync and search",
//       });
//       setProject(res.data);
//       setOutputs(res.data.results || []);
//       const start = performance.now();
//       const end = performance.now();
//       setMetrics(
//         res.data.results.reduce((acc, r, i) => {
//           acc[r.agent] = { duration: (Math.random() * 5) + 1 };
//           return acc;
//         }, {})
//       );
//       setLoading(false);
//     } catch (err) {
//       console.error(err);
//       setLoading(false);
//     }
//   };

//   const downloadResults = () => {
//     const blob = new Blob([JSON.stringify(project, null, 2)], { type: "application/json" });
//     const url = URL.createObjectURL(blob);
//     const a = document.createElement("a");
//     a.href = url;
//     a.download = `${project?.project_title || "results"}.json`;
//     a.click();
//     URL.revokeObjectURL(url);
//   };

//   return (
//     <div className="relative min-h-screen overflow-hidden">
//       <BackgroundParticles />
//       <GlassHeader project={project} duration={10} />

//       <main className="relative z-10 p-6 max-w-5xl mx-auto space-y-6">
//         <div className="flex justify-end gap-3">
//           <button
//             onClick={runWorkflow}
//             className="px-4 py-2 bg-indigo-600 text-white rounded-lg hover:brightness-110 transition"
//             disabled={loading}
//           >
//             {loading ? "Running..." : "▶ Run Workflow"}
//           </button>
//           {project && (
//             <button
//               onClick={downloadResults}
//               className="px-4 py-2 bg-green-600 text-white rounded-lg hover:brightness-110 transition"
//             >
//               ⬇ Download
//             </button>
//           )}
//         </div>

//         <div ref={scrollRef} className="space-y-4 overflow-y-auto max-h-[600px]">
//           {outputs.map((r, i) => (
//             <AgentOutputCard
//               key={i}
//               agent={r.agent}
//               content={r.content}
//               isActive={i === outputs.length - 1 && loading}
//             />
//           ))}
//         </div>

//         <AgentMetricsChart metrics={metrics} />
//       </main>
//     </div>
//   );
// }


import { useState, useRef } from "react";
import { runWorkflow } from "../api/client";
import GlassHeader from "../components/GlassHeader";
import BackgroundParticles from "../components/BackgroundParticles";
import AgentOutputCard from "../components/AgentOutputCard";
import AgentMetricsChart from "../components/AgentMetricsChart";

export default function Home() {
  const [title, setTitle] = useState("");
  const [prompt, setPrompt] = useState("");
  const [outputs, setOutputs] = useState([]);
  const [project, setProject] = useState(null);
  const [loading, setLoading] = useState(false);
  const [metrics, setMetrics] = useState({});
  const scrollRef = useRef(null);

  const runWorkflowHandler = async () => {
    if (!title.trim() || !prompt.trim()) {
      alert("Please enter both title and prompt.");
      return;
    }

    setLoading(true);
    try {
      const res = await runWorkflow(title, prompt);

      setProject(res);
      setOutputs(res.results || []);

      const durations = {};
      res.results?.forEach((r) => {
        durations[r.agent] = { duration: (Math.random() * 5 + 1).toFixed(2) };
      });
      setMetrics(durations);
    } catch (err) {
      console.error(err);
      alert("Workflow failed: " + (err.message || "Unknown error"));
    } finally {
      setLoading(false);
    }
  };

  const downloadResults = () => {
    const blob = new Blob([JSON.stringify(project, null, 2)], {
      type: "application/json",
    });
    const url = URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = `${project?.project_title || "results"}.json`;
    a.click();
    URL.revokeObjectURL(url);
  };

  return (
    <div className="relative min-h-screen overflow-hidden bg-gradient-to-br from-slate-950 via-indigo-950 to-purple-900 text-gray-100">
      <BackgroundParticles />
      <GlassHeader project={project} duration={10} />

      <main className="relative z-10 p-6 max-w-5xl mx-auto space-y-8">
        {/* Input section */}
        <div className="bg-white/10 backdrop-blur-md p-6 rounded-xl shadow-lg border border-white/10">
          <h2 className="text-lg font-semibold mb-4">Enter Workflow Details</h2>

          <input
            type="text"
            value={title}
            onChange={(e) => setTitle(e.target.value)}
            placeholder="Enter project title..."
            className="w-full p-3 rounded-md bg-white/10 border border-white/20 text-gray-100 placeholder-gray-400 mb-3 focus:ring-2 focus:ring-indigo-400 outline-none"
          />

          <textarea
            value={prompt}
            onChange={(e) => setPrompt(e.target.value)}
            placeholder="Enter project prompt..."
            rows="4"
            className="w-full p-3 rounded-md bg-white/10 border border-white/20 text-gray-100 placeholder-gray-400 focus:ring-2 focus:ring-indigo-400 outline-none"
          />

          <div className="flex justify-end gap-3 mt-4">
            <button
              onClick={runWorkflowHandler}
              disabled={loading}
              className="px-5 py-2 bg-indigo-600 text-white rounded-xl shadow-md hover:scale-105 hover:shadow-lg transition-all duration-200 disabled:opacity-50"
            >
              {loading ? "Running..." : "🚀 Run Workflow"}
            </button>
            {project && (
              <button
                onClick={downloadResults}
                className="px-5 py-2 bg-green-600 text-white rounded-xl shadow-md hover:scale-105 hover:shadow-lg transition-all duration-200"
              >
                ⬇ Download JSON
              </button>
            )}
          </div>
        </div>

        {/* Output section */}
        <div
          ref={scrollRef}
          className="space-y-4 overflow-y-auto max-h-[600px] p-4 backdrop-blur-lg rounded-lg bg-white/5 shadow-inner border border-white/10"
        >
          {outputs.length === 0 && !loading && (
            <p className="text-center text-gray-400 italic">
              Run the workflow to view agent responses...
            </p>
          )}
          {outputs.map((r, i) => (
            <AgentOutputCard
              key={i}
              agent={r.agent}
              content={r.content}
              isActive={i === outputs.length - 1 && loading}
            />
          ))}
        </div>

        {/* Chart section */}
        {outputs.length > 0 && <AgentMetricsChart metrics={metrics} />}
      </main>
    </div>
  );
}
