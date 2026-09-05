"use client";

import { useState, useEffect, useRef } from "react";
import { Send, Shield, Terminal, Database, Server, Clock, Mic, MicOff } from "lucide-react";
import { format } from "date-fns";

type Message = { role: "user" | "model"; content: string };
type Product = { id: string; name: string; price: number; stock: number };
type AuditLog = { id: string; action: string; status: string; details: any; time: string };

export default function AgenticCommerceDashboard() {
  const [activeTab, setActiveTab] = useState<"chat" | "ledger">("chat");
  const [messages, setMessages] = useState<Message[]>([
    { role: "model", content: "Agentic Commerce Gateway online. I am authorized to negotiate bulk purchases for RTX 4090s and ThinkPads. How can I help?" }
  ]);
  const [input, setInput] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  const [isListening, setIsListening] = useState(false);
  const [inventory, setInventory] = useState<Product[]>([]);
  const [logs, setLogs] = useState<AuditLog[]>([]);
  const chatEndRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    chatEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  const fetchLedger = async () => {
    try {
      // Remember to change these to your Ngrok backend URL if deploying!
      const [invRes, logRes] = await Promise.all([
        fetch("http://localhost:8000/api/inventory"),
        fetch("http://localhost:8000/api/audit")
      ]);
      setInventory(await invRes.json());
      setLogs(await logRes.json());
    } catch (e) {
      console.error("Ledger fetch failed", e);
    }
  };

  useEffect(() => {
    if (activeTab === "ledger") fetchLedger();
  }, [activeTab]);

  // Voice Recognition Logic
  const startListening = () => {
    // @ts-ignore - Web Speech API vendor prefixes
    const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
    if (!SpeechRecognition) {
      alert("Your browser does not support Voice AI transcription.");
      return;
    }
    const recognition = new SpeechRecognition();
    recognition.continuous = false;
    recognition.interimResults = false;
    recognition.lang = 'en-US';

    recognition.onstart = () => setIsListening(true);
    recognition.onresult = (event: any) => {
      const transcript = event.results[0][0].transcript;
      setInput(prev => prev + " " + transcript);
    };
    recognition.onend = () => setIsListening(false);
    recognition.onerror = () => setIsListening(false);

    recognition.start();
  };

  const sendMessage = async (e?: React.FormEvent) => {
    if (e) e.preventDefault();
    if (!input.trim() || isLoading) return;

    const newMsgs = [...messages, { role: "user" as const, content: input.trim() }];
    setMessages(newMsgs);
    setInput("");
    setIsLoading(true);

    try {
      // Remember to change this to your Ngrok backend URL if deploying!
      const res = await fetch("http://localhost:8000/api/chat", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ messages: newMsgs }),
      });
      const data = await res.json();
      setMessages([...newMsgs, { role: "model", content: data.reply }]);
    } catch (error) {
      setMessages([...newMsgs, { role: "model", content: "Error connecting to Agent Gateway." }]);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-zinc-950 text-zinc-300 font-mono flex flex-col">
      <header className="border-b border-zinc-800 bg-zinc-900/50 p-4 flex items-center justify-between">
        <div className="flex items-center gap-3 text-emerald-400">
          <Shield className="w-6 h-6" />
          <h1 className="text-xl font-bold tracking-tight text-zinc-100">Agentic Commerce Gateway</h1>
        </div>
        <div className="flex gap-2">
          <button onClick={() => setActiveTab("chat")} className={`px-4 py-2 text-sm rounded transition-colors ${activeTab === "chat" ? "bg-emerald-500/10 text-emerald-400 border border-emerald-500/20" : "hover:bg-zinc-800"}`}><Terminal className="w-4 h-4 inline mr-2" /> B2B Chat</button>
          <button onClick={() => setActiveTab("ledger")} className={`px-4 py-2 text-sm rounded transition-colors ${activeTab === "ledger" ? "bg-emerald-500/10 text-emerald-400 border border-emerald-500/20" : "hover:bg-zinc-800"}`}><Database className="w-4 h-4 inline mr-2" /> Audit Ledger</button>
        </div>
      </header>

      <main className="flex-1 overflow-hidden flex">
        {activeTab === "chat" ? (
          <div className="flex-1 flex flex-col max-w-4xl mx-auto w-full p-4">
            <div className="flex-1 overflow-y-auto space-y-4 pb-4 scrollbar-thin">
              {messages.map((m, i) => (
                <div key={i} className={`flex ${m.role === "user" ? "justify-end" : "justify-start"}`}>
                  <div className={`max-w-[80%] rounded-lg p-4 ${m.role === "user" ? "bg-zinc-800 text-zinc-100" : "bg-emerald-950/30 border border-emerald-900/50 text-zinc-300 whitespace-pre-wrap"}`}>
                    {m.content}
                  </div>
                </div>
              ))}
              {isLoading && (
                <div className="flex justify-start">
                  <div className="bg-emerald-950/30 border border-emerald-900/50 rounded-lg p-4 text-emerald-500 animate-pulse">Evaluating strict constraints...</div>
                </div>
              )}
              <div ref={chatEndRef} />
            </div>
            
            <form onSubmit={sendMessage} className="relative mt-4 flex gap-2">
              <div className="relative flex-1">
                <input
                  type="text"
                  value={input}
                  onChange={(e) => setInput(e.target.value)}
                  placeholder="Type or speak a bulk order negotiation..."
                  className="w-full bg-zinc-900 border border-zinc-800 rounded-lg pl-4 pr-12 py-4 focus:outline-none focus:border-emerald-500/50 text-zinc-100"
                />
                <button 
                  type="button" 
                  onClick={startListening}
                  className={`absolute right-3 top-3 p-2 rounded-full transition-colors ${isListening ? "bg-red-500/20 text-red-500 animate-pulse" : "text-zinc-400 hover:text-zinc-100"}`}
                >
                  {isListening ? <MicOff className="w-5 h-5" /> : <Mic className="w-5 h-5" />}
                </button>
              </div>
              <button type="submit" disabled={isLoading} className="p-4 bg-emerald-600 hover:bg-emerald-500 text-white rounded-lg transition-colors disabled:opacity-50">
                <Send className="w-5 h-5" />
              </button>
            </form>
          </div>
        ) : (
          <div className="flex-1 overflow-y-auto p-6 max-w-6xl mx-auto w-full space-y-8">
            {/* Same Audit Ledger UI as before... */}
            <section>
              <h2 className="text-lg text-zinc-100 flex items-center gap-2 mb-4"><Server className="w-5 h-5" /> Live Inventory (Gatekeeper)</h2>
              <div className="border border-zinc-800 rounded-lg overflow-hidden">
                <table className="w-full text-left text-sm">
                  <thead className="bg-zinc-900 border-b border-zinc-800">
                    <tr><th className="p-3">Product</th><th className="p-3">Base Price</th><th className="p-3">Stock Limit</th></tr>
                  </thead>
                  <tbody>
                    {inventory.map(p => (
                      <tr key={p.id} className="border-b border-zinc-800/50">
                        <td className="p-3 font-medium text-zinc-200">{p.name}</td>
                        <td className="p-3">₹{p.price.toLocaleString()}</td>
                        <td className="p-3">
                          <span className={`px-2 py-1 rounded text-xs ${p.stock > 0 ? "bg-emerald-500/10 text-emerald-400" : "bg-red-500/10 text-red-400"}`}>
                            {p.stock} available
                          </span>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </section>

            <section>
              <h2 className="text-lg text-zinc-100 flex items-center gap-2 mb-4"><Clock className="w-5 h-5" /> Immutable Audit Ledger</h2>
              <div className="border border-zinc-800 rounded-lg overflow-hidden">
                <table className="w-full text-left text-sm">
                  <thead className="bg-zinc-900 border-b border-zinc-800">
                    <tr><th className="p-3">Timestamp</th><th className="p-3">Action</th><th className="p-3">Status</th><th className="p-3">Payload Details</th></tr>
                  </thead>
                  <tbody>
                    {logs.map(log => (
                      <tr key={log.id} className="border-b border-zinc-800/50">
                        <td className="p-3 whitespace-nowrap">{format(new Date(log.time), "HH:mm:ss")}</td>
                        <td className="p-3">{log.action}</td>
                        <td className="p-3">
                          <span className={`px-2 py-1 rounded text-xs ${log.status === "APPROVED" ? "bg-emerald-500/10 text-emerald-400" : log.status === "BLOCKED" ? "bg-red-500/10 text-red-500 font-bold" : "bg-yellow-500/10 text-yellow-400"}`}>
                            {log.status}
                          </span>
                        </td>
                        <td className="p-3 font-mono text-xs max-w-xs truncate">{JSON.stringify(log.details)}</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </section>
          </div>
        )}
      </main>
    </div>
  );
}