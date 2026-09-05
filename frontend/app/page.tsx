"use client";

import { useState, useEffect, useRef } from "react";
import { Send, Shield, Terminal, Database, Server, Clock, Mic, MicOff } from "lucide-react";
import { format } from "date-fns";
import { motion, AnimatePresence } from "framer-motion";

type Message = { role: "user" | "model"; content: string };
type Product = { id: string; name: string; price: number; stock: number };
type AuditLog = { id: string; action: string; status: string; details: any; time: string };

export default function AgenticCommerceDashboard() {
  const [activeTab, setActiveTab] = useState<"chat" | "ledger">("chat");
  const [messages, setMessages] = useState<Message[]>([
    { role: "model", content: "Agentic Commerce Gateway online. I am authorized to negotiate bulk purchases for our enterprise hardware catalog. How can I assist your procurement team today?" }
  ]);
  const [input, setInput] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  const [isListening, setIsListening] = useState(false);
  const [inventory, setInventory] = useState<Product[]>([]);
  const [logs, setLogs] = useState<AuditLog[]>([]);
  const chatEndRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    chatEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages, isLoading]);

  const fetchLedger = async () => {
    try {
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

  const startListening = () => {
    // @ts-ignore
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
    <div className="min-h-screen bg-zinc-950 text-zinc-300 font-sans flex flex-col selection:bg-emerald-500/30">
      <header className="sticky top-0 z-50 border-b border-zinc-800/50 bg-zinc-950/80 backdrop-blur-md p-4 flex items-center justify-between">
        <div className="flex items-center gap-3 text-emerald-400">
          <Shield className="w-6 h-6" />
          <h1 className="text-xl font-bold tracking-tight text-zinc-100 font-mono">Agentic Commerce Gateway</h1>
        </div>
        <div className="flex gap-2">
          <button onClick={() => setActiveTab("chat")} className={`px-4 py-2 text-sm font-medium rounded-md transition-all ${activeTab === "chat" ? "bg-emerald-500/10 text-emerald-400 border border-emerald-500/20 shadow-[0_0_15px_rgba(16,185,129,0.1)]" : "hover:bg-zinc-900 text-zinc-400"}`}><Terminal className="w-4 h-4 inline mr-2" /> B2B Chat</button>
          <button onClick={() => setActiveTab("ledger")} className={`px-4 py-2 text-sm font-medium rounded-md transition-all ${activeTab === "ledger" ? "bg-emerald-500/10 text-emerald-400 border border-emerald-500/20 shadow-[0_0_15px_rgba(16,185,129,0.1)]" : "hover:bg-zinc-900 text-zinc-400"}`}><Database className="w-4 h-4 inline mr-2" /> Audit Ledger</button>
        </div>
      </header>

      <main className="flex-1 overflow-hidden flex relative">
        <div className="absolute inset-0 bg-[radial-gradient(ellipse_at_top,_var(--tw-gradient-stops))] from-zinc-900/20 via-zinc-950 to-zinc-950 pointer-events-none" />
        
        {activeTab === "chat" ? (
          <div className="flex-1 flex flex-col max-w-4xl mx-auto w-full p-4 relative z-10">
            <div className="flex-1 overflow-y-auto space-y-6 pb-4 scrollbar-thin">
              <AnimatePresence>
                {messages.map((m, i) => (
                  <motion.div 
                    initial={{ opacity: 0, y: 10 }}
                    animate={{ opacity: 1, y: 0 }}
                    key={i} 
                    className={`flex ${m.role === "user" ? "justify-end" : "justify-start"}`}
                  >
                    <div className={`max-w-[80%] rounded-2xl p-4 text-sm leading-relaxed shadow-sm ${m.role === "user" ? "bg-zinc-800 text-zinc-100 rounded-br-sm" : "bg-zinc-900/80 border border-zinc-800 text-zinc-300 rounded-bl-sm whitespace-pre-wrap"}`}>
                      {m.content}
                    </div>
                  </motion.div>
                ))}
                {isLoading && (
                  <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }} className="flex justify-start">
                    <div className="bg-zinc-900/80 border border-zinc-800 rounded-2xl rounded-bl-sm p-4 flex gap-1 items-center h-[52px]">
                      <motion.div className="w-2 h-2 bg-emerald-500 rounded-full" animate={{ y: [0, -5, 0] }} transition={{ repeat: Infinity, duration: 0.6, delay: 0 }} />
                      <motion.div className="w-2 h-2 bg-emerald-500 rounded-full" animate={{ y: [0, -5, 0] }} transition={{ repeat: Infinity, duration: 0.6, delay: 0.2 }} />
                      <motion.div className="w-2 h-2 bg-emerald-500 rounded-full" animate={{ y: [0, -5, 0] }} transition={{ repeat: Infinity, duration: 0.6, delay: 0.4 }} />
                    </div>
                  </motion.div>
                )}
              </AnimatePresence>
              <div ref={chatEndRef} />
            </div>
            
            <form onSubmit={sendMessage} className="relative mt-4 flex gap-2">
              <div className="relative flex-1">
                <input
                  type="text"
                  value={input}
                  onChange={(e) => setInput(e.target.value)}
                  placeholder="Type or speak your hardware requirements..."
                  className="w-full bg-zinc-900/90 backdrop-blur-sm border border-zinc-800 rounded-xl pl-4 pr-12 py-4 focus:outline-none focus:border-emerald-500/50 focus:ring-1 focus:ring-emerald-500/50 text-zinc-100 transition-all shadow-lg"
                />
                <button 
                  type="button" 
                  onClick={startListening}
                  className={`absolute right-3 top-3 p-2 rounded-full transition-colors ${isListening ? "bg-emerald-500/20 text-emerald-400 animate-pulse" : "text-zinc-500 hover:text-zinc-300"}`}
                >
                  {isListening ? <MicOff className="w-5 h-5" /> : <Mic className="w-5 h-5" />}
                </button>
              </div>
              <button type="submit" disabled={isLoading} className="p-4 bg-emerald-600 hover:bg-emerald-500 text-white rounded-xl transition-colors disabled:opacity-50 shadow-lg shadow-emerald-900/20">
                <Send className="w-5 h-5" />
              </button>
            </form>
          </div>
        ) : (
          <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }} className="flex-1 overflow-y-auto p-6 max-w-6xl mx-auto w-full space-y-8 relative z-10">
            {/* Same Audit Ledger UI, but styled to match the new aesthetic */}
            <section>
              <h2 className="text-lg text-zinc-100 flex items-center gap-2 mb-4 font-mono"><Server className="w-5 h-5 text-emerald-500" /> Production Inventory</h2>
              <div className="border border-zinc-800/50 rounded-xl overflow-hidden bg-zinc-900/30 backdrop-blur-sm">
                <table className="w-full text-left text-sm">
                  <thead className="bg-zinc-900/80 border-b border-zinc-800">
                    <tr><th className="p-4 font-medium text-zinc-400">SKU</th><th className="p-4 font-medium text-zinc-400">Base Price</th><th className="p-4 font-medium text-zinc-400">Stock Availability</th></tr>
                  </thead>
                  <tbody className="divide-y divide-zinc-800/50">
                    {inventory.map(p => (
                      <tr key={p.id} className="hover:bg-zinc-800/30 transition-colors">
                        <td className="p-4 font-medium text-zinc-200">{p.name}</td>
                        <td className="p-4 text-zinc-300 font-mono">₹{p.price.toLocaleString()}</td>
                        <td className="p-4">
                          <span className={`px-2.5 py-1 rounded-full text-xs font-medium border ${p.stock > 0 ? "bg-emerald-500/10 text-emerald-400 border-emerald-500/20" : "bg-red-500/10 text-red-400 border-red-500/20"}`}>
                            {p.stock} units
                          </span>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </section>

            <section>
              <h2 className="text-lg text-zinc-100 flex items-center gap-2 mb-4 font-mono"><Clock className="w-5 h-5 text-emerald-500" /> Immutable Audit Ledger</h2>
              <div className="border border-zinc-800/50 rounded-xl overflow-hidden bg-zinc-900/30 backdrop-blur-sm">
                <table className="w-full text-left text-sm">
                  <thead className="bg-zinc-900/80 border-b border-zinc-800">
                    <tr><th className="p-4 font-medium text-zinc-400">Timestamp</th><th className="p-4 font-medium text-zinc-400">Agent Action</th><th className="p-4 font-medium text-zinc-400">Status</th><th className="p-4 font-medium text-zinc-400">Payload Details</th></tr>
                  </thead>
                  <tbody className="divide-y divide-zinc-800/50">
                    {logs.map(log => (
                      <tr key={log.id} className="hover:bg-zinc-800/30 transition-colors">
                        <td className="p-4 whitespace-nowrap text-zinc-400 font-mono">{format(new Date(log.time), "HH:mm:ss")}</td>
                        <td className="p-4 text-zinc-300">{log.action}</td>
                        <td className="p-4">
                          <span className={`px-2.5 py-1 rounded-full text-xs font-medium border ${log.status === "APPROVED" ? "bg-emerald-500/10 text-emerald-400 border-emerald-500/20" : log.status === "BLOCKED" ? "bg-red-500/10 text-red-500 border-red-500/20" : "bg-yellow-500/10 text-yellow-400 border-yellow-500/20"}`}>
                            {log.status}
                          </span>
                        </td>
                        <td className="p-4 font-mono text-xs max-w-xs truncate text-zinc-500">{JSON.stringify(log.details)}</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </section>
          </motion.div>
        )}
      </main>
    </div>
  );
}