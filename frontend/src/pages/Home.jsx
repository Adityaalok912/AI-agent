import { useState, useRef, useEffect } from "react";
// We will use fetch directly for the new API structure
// import { runWorkflow } from "../api/client"; 
import GlassHeader from "../components/GlassHeader";
import BackgroundParticles from "../components/BackgroundParticles";
import AgentOutputCard from "../components/AgentOutputCard";
import AgentMetricsChart from "../components/AgentMetricsChart";
import { Loader2 } from "lucide-react";

// It's good practice to have a dedicated component for different message types
const AgentStatusMessage = ({ message }) => {
    let content = null;
    switch (message.event_type) {
        case 'workflow_start':
            content = `🚀 Workflow started for project: ${message.content}`;
            break;
        case 'agent_start':
            content = <><Loader2 className="h-4 w-4 mr-2 animate-spin" />{message.content}</>;
            break;
        case 'workflow_end':
            content = `✅ ${message.content}`;
            break;
        case 'error':
            content = `🔥 Error: ${message.content}`;
            break;
        default:
            return null; // Don't render anything for agent_result, as AgentOutputCard will handle it
    }
    return <p className="text-center text-gray-400 italic flex items-center justify-center">{content}</p>;
};

export default function Home() {
    const [title, setTitle] = useState("");
    const [prompt, setPrompt] = useState("");
    const [messages, setMessages] = useState([]); // Will store all incoming event messages
    const [project, setProject] = useState(null); // Stores basic project info
    const [workflowStatus, setWorkflowStatus] = useState('idle'); // idle, running, finished, error
    const [metrics, setMetrics] = useState({});
    
    const scrollRef = useRef(null);
    const eventSourceRef = useRef(null);

    // Effect to auto-scroll as new messages arrive
    useEffect(() => {
        if (scrollRef.current) {
            scrollRef.current.scrollTop = scrollRef.current.scrollHeight;
        }
    }, [messages]);

    // Main effect for handling the Server-Sent Events (SSE) connection
    useEffect(() => {
        if (workflowStatus !== 'running' || !project?.project_id) {
            return;
        }

        const eventSource = new EventSource(`/api/agents/stream/${project.project_id}`);
        eventSourceRef.current = eventSource;

        eventSource.onopen = () => console.log("SSE connection established.");

        eventSource.addEventListener('agent_update', (event) => {
            const newMessage = JSON.parse(event.data);

            setMessages(prev => [...prev, newMessage]);

            // If it's a final agent result, update metrics
            if (newMessage.event_type === 'agent_result') {
                 setMetrics(prevMetrics => ({
                    ...prevMetrics,
                    [newMessage.agent_name]: { duration: (Math.random() * 5 + 1) } // Using random as before
                 }));
            }
            
            if (newMessage.event_type === 'workflow_end' || newMessage.event_type === 'error') {
                setWorkflowStatus('finished');
                eventSource.close();
            }
        });

        eventSource.onerror = (err) => {
            console.error("EventSource failed:", err);
            setWorkflowStatus('error');
            eventSource.close();
        };

        // Cleanup function to close connection on component unmount or re-run
        return () => {
            if (eventSource) {
                eventSource.close();
            }
        };
    }, [workflowStatus, project?.project_id]);


    const runWorkflowHandler = async () => {
        if (!title.trim() || !prompt.trim()) {
            alert("Please enter both title and prompt.");
            return;
        }

        // Reset state for a new run
        setMessages([]);
        setMetrics({});
        setProject(null);
        setWorkflowStatus('running');

        try {
            // This API call now returns immediately
            const response = await fetch('/api/agents/run', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ title, prompt }),
            });

            if (!response.ok) {
                const errorData = await response.json();
                throw new Error(errorData.detail || `HTTP error! status: ${response.status}`);
            }

            const data = await response.json();
            // Set project info; this triggers the useEffect to connect to the stream
            setProject({ project_id: data.project_id, project_title: data.project_title });

        } catch (err) {
            console.error(err);
            alert("Failed to start workflow: " + (err.message || "Unknown error"));
            setWorkflowStatus('error');
        }
    };
    
    const stopWorkflowHandler = () => {
        if (eventSourceRef.current) {
            eventSourceRef.current.close();
            console.log("SSE connection closed by user.");
        }
        setWorkflowStatus('finished');
    };

    const downloadResults = () => {
        const resultsOnly = messages.filter(m => m.event_type === 'agent_result');
        const dataToDownload = {
            project_id: project.project_id,
            project_title: project.project_title,
            results: resultsOnly.map(r => ({ agent: r.agent_name, content: r.content })),
        };
        const blob = new Blob([JSON.stringify(dataToDownload, null, 2)], {
            type: "application/json",
        });
        const url = URL.createObjectURL(blob);
        const a = document.createElement("a");
        a.href = url;
        a.download = `${project?.project_title || "results"}.json`;
        a.click();
        URL.revokeObjectURL(url);
    };
    
    const finalOutputs = messages.filter(m => m.event_type === 'agent_result');

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
                        disabled={workflowStatus === 'running'}
                    />
                    <textarea
                        value={prompt}
                        onChange={(e) => setPrompt(e.target.value)}
                        placeholder="Enter project prompt..."
                        rows="4"
                        className="w-full p-3 rounded-md bg-white/10 border border-white/20 text-gray-100 placeholder-gray-400 focus:ring-2 focus:ring-indigo-400 outline-none"
                        disabled={workflowStatus === 'running'}
                    />
                    <div className="flex justify-end gap-3 mt-4">
                        {workflowStatus !== 'running' ? (
                             <button
                                onClick={runWorkflowHandler}
                                disabled={!title || !prompt}
                                className="px-5 py-2 bg-indigo-600 text-white rounded-xl shadow-md hover:scale-105 hover:shadow-lg transition-all duration-200 disabled:opacity-50"
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
                        {project && finalOutputs.length > 0 && (
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
                    {messages.length === 0 && workflowStatus === 'idle' && (
                        <p className="text-center text-gray-400 italic">
                            Run the workflow to view agent responses...
                        </p>
                    )}
                    {messages.map((msg, i) => 
                        msg.event_type === 'agent_result' ? (
                            <AgentOutputCard
                                key={i}
                                agent={msg.agent_name}
                                content={msg.content}
                                isActive={false} // Can be enhanced later if needed
                            />
                        ) : (
                            <AgentStatusMessage key={i} message={msg} />
                        )
                    )}
                    {workflowStatus === 'running' && messages.length === 0 && (
                         <p className="text-center text-gray-400 italic flex items-center justify-center"><Loader2 className="h-4 w-4 mr-2 animate-spin" />Waiting for workflow to start...</p>
                    )}
                </div>

                {/* Chart section */}
                {Object.keys(metrics).length > 0 && <AgentMetricsChart metrics={metrics} />}
            </main>
        </div>
    );
}