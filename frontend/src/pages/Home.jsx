import { useEffect, useMemo, useRef, useState } from "react";
import GlassHeader from "../components/GlassHeader";
import BackgroundParticles from "../components/BackgroundParticles";
import AgentOutputCard from "../components/AgentOutputCard";
import AgentMetricsChart from "../components/AgentMetricsChart";
import { Loader2 } from "lucide-react";
import useStopwatch from "../hooks/useStopwatch";

// Status message renderer
const AgentStatusMessage = ({ message }) => {
  let content = null;
  switch (message.event_type) {
    case "workflow_start":
      content = `🚀 Workflow started for project: ${message.content}`;
      break;
    case "agent_start":
      content = (
        <>
          <Loader2 className="h-4 w-4 mr-2 animate-spin" />
          {message.content}
        </>
      );
      break;
    case "workflow_end":
      content = `✅ ${message.content}`;
      break;
    case "error":
      content = `🔥 Error: ${message.content}`;
      break;
    default:
      return null;
  }
  return (
    <p className="text-center text-gray-600 dark:text-gray-400 italic flex items-center justify-center">
      {content}
    </p>
  );
};

// Normalize agent names so "X (Refined)" and "X - Refined" map to "X"
const normalizeAgentName = (name = "") => {
  let n = String(name).trim();
  n = n.replace(/\s*\(refined\)\s*$/i, "");
  n = n.replace(/\s*[-–]\s*refined\s*$/i, "");
  n = n.replace(/\s*refined\s*$/i, "");
    n = n.replace(/\s*final\s*$/i, "");
  n = n.replace(/\s*[-–]\s*final\s*$/i, "");
  n = n.replace(/\s*\(final\)\s*$/i, "");
  return n.trim();
};

const isOrchestrator = (name = "") => /orchestrator/i.test(normalizeAgentName(name));

export default function Home() {
  const [title, setTitle] = useState("");
  const [prompt, setPrompt] = useState("");
  const [messages, setMessages] = useState([]); // raw stream (for status/metrics)
  const [project, setProject] = useState(null);
  const [workflowStatus, setWorkflowStatus] = useState("idle");
  const [metrics, setMetrics] = useState({});
  // Latest response per agent (replaces previous)
  const [agentOutputs, setAgentOutputs] = useState({}); // { [agent]: { content, inProgress, updatedAt } }
  const [selectedAgent, setSelectedAgent] = useState("");

  // Stopwatch for header
  const { elapsedSeconds, isRunning, start, stop, reset } = useStopwatch();

  const scrollRef = useRef(null);
  const eventSourceRef = useRef(null);

  // Scroll to top when switching selected agent (optional, if using tab view)
  useEffect(() => {
    if (scrollRef.current) scrollRef.current.scrollTo({ top: 0 });
  }, [selectedAgent]);

  // SSE stream
  useEffect(() => {
    if (workflowStatus !== "running" || !project?.project_id) return;

    const eventSource = new EventSource(`/api/agents/stream/${project.project_id}`);
    eventSourceRef.current = eventSource;

    eventSource.onopen = () => console.log("SSE connection established.");

    eventSource.addEventListener("agent_update", (event) => {
      const newMessage = JSON.parse(event.data);
      setMessages((prev) => [...prev, newMessage]);

      const raw = newMessage.agent_name;
      const baseAgent = normalizeAgentName(raw);

      // Skip orchestrator in outputs
      if (baseAgent && !isOrchestrator(baseAgent)) {
        setAgentOutputs((prev) => {
          const prevEntry = prev[baseAgent] || { content: "", inProgress: false, updatedAt: 0 };
          const next = { ...prev };

          if (newMessage.event_type === "agent_start") {
            // Keep previous content visible while starting; mark as in progress
            next[baseAgent] = { ...prevEntry, inProgress: true, updatedAt: Date.now() };
          } else if (newMessage.event_type === "agent_result") {
            // Refined (or fresh) result REPLACES previous content
            next[baseAgent] = {
              content: newMessage.content || "",
              inProgress: false,
              updatedAt: Date.now(),
            };
          }
          return next;
        });
      }

      // Metrics keyed by normalized agent
      if (newMessage.event_type === "agent_result" && baseAgent && !isOrchestrator(baseAgent)) {
        setMetrics((prevMetrics) => ({
          ...prevMetrics,
          [baseAgent]: { duration: Math.random() * 5 + 1 }, // placeholder
        }));
      }

      // Stop the stopwatch when workflow ends or on error
      if (newMessage.event_type === "workflow_end" || newMessage.event_type === "error") {
        setWorkflowStatus("finished");
        stop();
        eventSource.close();
      }
    });

    eventSource.onerror = (err) => {
      console.error("EventSource failed:", err);
      setWorkflowStatus("error");
      stop();
      eventSource.close();
    };

    return () => {
      if (eventSource) eventSource.close();
    };
  }, [workflowStatus, project?.project_id, stop]);

  const runWorkflowHandler = async () => {
    if (!title.trim() || !prompt.trim()) {
      alert("Please enter both title and prompt.");
      return;
    }

    // Reset state
    setMessages([]);
    setMetrics({});
    setAgentOutputs({});
    setSelectedAgent("");
    setProject(null);

    // Start stopwatch fresh
    reset();
    start();

    setWorkflowStatus("running");

    try {
      const response = await fetch("/api/agents/run", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ title, prompt }),
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || `HTTP error! status: ${response.status}`);
      }

      const data = await response.json();
      setProject({ project_id: data.project_id, project_title: data.project_title });
    } catch (err) {
      console.error(err);
      alert("Failed to start workflow: " + (err.message || "Unknown error"));
      setWorkflowStatus("error");
      stop();
    }
  };

  const stopWorkflowHandler = () => {
    if (eventSourceRef.current) {
      eventSourceRef.current.close();
      console.log("SSE connection closed by user.");
    }
    setWorkflowStatus("finished");
    stop();
  };

  const downloadResults = () => {
    const results = Object.entries(agentOutputs).map(([agent, o]) => ({
      agent,
      content: o.content,
    }));
    const dataToDownload = {
      project_id: project?.project_id,
      project_title: project?.project_title,
      results,
    };
    const blob = new Blob([JSON.stringify(dataToDownload, null, 2)], { type: "application/json" });
    const url = URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = `${project?.project_title || "results"}.json`;
    a.click();
    URL.revokeObjectURL(url);
  };

  // Agents to display in tabs (exclude orchestrator)
  const visibleAgents = useMemo(
    () => Object.keys(agentOutputs).filter((a) => !isOrchestrator(a)),
    [agentOutputs]
  );

  useEffect(() => {
    if (!selectedAgent && visibleAgents.length > 0) {
      setSelectedAgent(visibleAgents[0]);
    } else if (selectedAgent && !visibleAgents.includes(selectedAgent)) {
      setSelectedAgent(visibleAgents[0] || "");
    }
  }, [visibleAgents, selectedAgent]);

  return (
    <div
      id="homeroot"
      className="
        relative min-h-screen overflow-hidden
        bg-gradient-to-br from-indigo-50 to-slate-200
        dark:from-[#3b0764] dark:to-[#1b192f]
      "
    >
      <BackgroundParticles />

      {/* Pass stopwatch state into header */}
      <GlassHeader
        project={project}
        isRunning={isRunning}
        elapsedSeconds={elapsedSeconds}
      />

      {/* Let responses use max available width */}
      <main className="relative z-10 p-6 w-full max-w-7xl mx-auto space-y-8">
        {/* Input section */}
        <div className="bg-slate-100/70 dark:bg-slate-900/70 backdrop-blur-md p-6 rounded-xl shadow-lg border border-slate-200 dark:border-slate-700">
          <h2 className="text-lg font-semibold mb-4 text-slate-800 dark:text-slate-100">
            Enter Workflow Details
          </h2>
          <input
            type="text"
            value={title}
            onChange={(e) => setTitle(e.target.value)}
            placeholder="Enter project title..."
            className="w-full p-3 rounded-md text-slate-900 dark:text-slate-100 bg-white/80 dark:bg-slate-800/80 border border-slate-300 dark:border-slate-600 placeholder-slate-500 dark:placeholder-slate-400 focus:ring-2 focus:ring-indigo-500 outline-none transition-colors"
            disabled={workflowStatus === "running"}
          />
          <textarea
            value={prompt}
            onChange={(e) => setPrompt(e.target.value)}
            placeholder="Enter project prompt..."
            rows="4"
            className="w-full p-3 mt-3 rounded-md text-slate-900 dark:text-slate-100 bg-white/80 dark:bg-slate-800/80 border border-slate-300 dark:border-slate-600 placeholder-slate-500 dark:placeholder-slate-400 focus:ring-2 focus:ring-indigo-500 outline-none transition-colors"
            disabled={workflowStatus === "running"}
          />
          <div className="flex justify-end gap-3 mt-4">
            {workflowStatus !== "running" ? (
              <button
                onClick={runWorkflowHandler}
                disabled={!title || !prompt}
                className="px-5 py-2 bg-violet-600 text-white rounded-xl shadow-md hover:scale-105 hover:shadow-lg transition-all duration-200 disabled:opacity-50 focus:ring-2 focus:ring-violet-500"
              >
                🚀 Run Workflow
              </button>
            ) : (
              <button
                onClick={stopWorkflowHandler}
                className="px-5 py-2 bg-red-600 text-white rounded-xl shadow-md hover:scale-105 hover:shadow-lg transition-all duration-200"
              >
                🛑 Stop Workflow
              </button>
            )}
            {project && Object.keys(agentOutputs).length > 0 && (
              <button
                onClick={downloadResults}
                className="px-5 py-2 bg-green-600 text-white rounded-xl shadow-md hover:scale-105 hover:shadow-lg transition-all duration-200"
              >
                ⬇ Download JSON
              </button>
            )}
          </div>
        </div>

        {/* Responses area – tabbed agents (names) and full-width content */}
        <div
          ref={scrollRef}
          className="w-full overflow-y-auto max-h-[600px] p-4 backdrop-blur-lg rounded-lg bg-slate-100/60 dark:bg-slate-900/60 shadow-inner border border-slate-200 dark:border-slate-700"
        >
          {visibleAgents.length === 0 && workflowStatus === "idle" && (
            <p className="text-center text-slate-600 dark:text-slate-400 italic">
              Run the workflow to view agent responses...
            </p>
          )}

          {visibleAgents.length > 0 && (
            <>
              <div role="tablist" aria-label="Agents" className="mb-4 flex flex-wrap gap-2">
                {visibleAgents.map((agent) => {
                  const entry = agentOutputs[agent] || { content: "", inProgress: false };
                  const active = selectedAgent === agent;
                  return (
                    <button
                      key={`tab-${agent}`}
                      role="tab"
                      aria-selected={active}
                      onClick={() => setSelectedAgent(agent)}
                      className={[
                        "group relative inline-flex items-center gap-2 px-3 py-1.5 rounded-full border transition-colors",
                        active
                          ? "bg-violet-600 text-white border-violet-500"
                          : "bg-white/70 dark:bg-slate-800/70 text-slate-800 dark:text-slate-200 border-slate-300 dark:border-slate-600 hover:bg-white/90 dark:hover:bg-slate-700/70",
                      ].join(" ")}
                      title={agent}
                    >
                      <span className="font-medium">{agent}</span>
                      {entry.inProgress ? (
                        <Loader2 className="h-3.5 w-3.5 animate-spin text-white/90 group-aria-selected:text-white" />
                      ) : (
                        <span className="h-2.5 w-2.5 rounded-full bg-emerald-500 inline-block" aria-hidden />
                      )}
                    </button>
                  );
                })}
              </div>

              {selectedAgent ? (
                <AgentOutputCard
                  key={selectedAgent}
                  agent={selectedAgent}
                  content={agentOutputs[selectedAgent]?.content || ""}
                  isActive={agentOutputs[selectedAgent]?.inProgress || false}
                />
              ) : (
                <p className="text-center text-slate-600 dark:text-slate-400 italic">
                  Select an agent to view its response.
                </p>
              )}
            </>
          )}

          {/* Workflow/global status messages (not per agent) */}
          <div className="mt-4 space-y-2">
            {messages
              .filter(
                (m) =>
                  !m.agent_name ||
                  m.event_type === "workflow_start" ||
                  m.event_type === "workflow_end" ||
                  m.event_type === "error"
              )
              .map((msg, i) => (
                <AgentStatusMessage key={`status-${i}`} message={msg} />
              ))}
            {workflowStatus === "running" && messages.length === 0 && (
              <p className="text-center text-slate-600 dark:text-slate-400 italic flex items-center justify-center">
                <Loader2 className="h-4 w-4 mr-2 animate-spin" />
                Waiting for workflow to start...
              </p>
            )}
          </div>
        </div>

        {/* Chart section */}
        {Object.keys(metrics).length > 0 && <AgentMetricsChart metrics={metrics} />}
      </main>
    </div>
  );
}