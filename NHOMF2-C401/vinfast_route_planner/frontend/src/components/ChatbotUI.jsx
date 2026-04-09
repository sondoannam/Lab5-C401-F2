import { useState, useRef, useEffect } from 'react';
import { Send, Zap, ShieldAlert, Bot, User } from 'lucide-react';

export default function ChatbotUI({ summary, warnings, feasible, setWorkflowResult, setIsLoading }) {
  const isError = feasible === false || (warnings && warnings.length > 0);
  const [messages, setMessages] = useState([]);
  const [inputVal, setInputVal] = useState("");
  const scrollContainerRef = useRef(null);

  const previousSummaryRef = useRef(null);
  const isFromChatRef = useRef(false);

  // Initialize or append static summary if it originates from outside (e.g. map click)
  useEffect(() => {
    if (summary && summary !== previousSummaryRef.current) {
      previousSummaryRef.current = summary;
      if (!isFromChatRef.current) {
        setMessages(prev => [...prev, { role: "assistant", content: cleanSummary(summary) }]);
      } else {
        isFromChatRef.current = false;
      }
    }
  }, [summary]);

  useEffect(() => {
    // Auto scroll without shifting the parent container
    if (scrollContainerRef.current) {
      const container = scrollContainerRef.current;
      container.scrollTo({ top: container.scrollHeight, behavior: 'smooth' });
    }
  }, [messages, warnings]);

  const cleanSummary = (text) => {
    if (!text) return "Sẵn sàng phân tích. Hãy hỏi tôi về lộ trình này!";
    let cleaned = text.replace(/NUMBER OF CHARGING STOPS:.*\n/g, ''); 
    cleaned = cleaned.replace(/SYSTEM WARNINGS:[\s\S]*/g, ''); 
    return cleaned.trim() || 'Hệ thống đã nhận lộ trình, bạn có muốn tối ưu lại không?';
  };

  const handleSendMessage = async () => {
    if (!inputVal.trim()) return;

    const userMessage = { role: "user", content: inputVal };
    const newMessages = [...messages, userMessage];
    setMessages(newMessages);
    setInputVal("");
    setIsLoading(true);

    try {
      const response = await fetch('http://localhost:8001/api/chat', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ messages: newMessages }),
      });
      
      if (!response.ok) {
        throw new Error(`API Error: ${response.status}`);
      }
      
      const data = await response.json();
      
      // Add assistant response
      setMessages([...newMessages, { role: "assistant", content: data.content }]);
      
      // If a route was planned by the agent via tool calling, update the map
      if (data.workflow_data && setWorkflowResult) {
         isFromChatRef.current = true;
         setWorkflowResult(data.workflow_data);
      }
    } catch (err) {
      setMessages([...newMessages, { role: "assistant", content: `Lỗi kết nối AI: ${err.message}` }]);
    } finally {
      setIsLoading(false);
    }
  };

  const handleKeyDown = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSendMessage();
    }
  };

  return (
    <div className={`flex-1 border ${isError ? 'border-amber-700/50' : 'border-slate-700/50'} bg-slate-900/60 rounded-2xl flex flex-col overflow-hidden backdrop-blur-xl shadow-lg relative min-h-[300px]`}>
      {/* Chat messages */}
      <div 
        ref={scrollContainerRef}
        className="flex-1 p-5 overflow-y-auto space-y-5 flex flex-col scrollbar-thin scrollbar-thumb-slate-800 scrollbar-track-transparent"
      >
         
         {messages.length === 0 && !summary && (
           <div className="text-slate-500 text-sm text-center my-auto">
             Hãy thử nhập: "Cho tôi lộ trình từ Hà Nội đi Đà Nẵng, xe còn khoảng 80% pin."
           </div>
         )}

         {messages.map((msg, i) => (
           <div key={i} className={`flex gap-3 ${msg.role === 'user' ? 'flex-row-reverse' : ''}`}>
              <div className={`w-9 h-9 rounded-full border flex items-center justify-center mt-1 shrink-0 ${
                  msg.role === 'user' ? 'bg-indigo-900/50 border-indigo-500/30' : 
                  (isError && i === 0) ? 'bg-amber-900/50 border-amber-500/30' : 'bg-emerald-900/50 border-emerald-500/30'
              }`}>
                 {msg.role === 'user' ? <User size={18} className="text-indigo-400" /> : <Bot size={18} className={(isError && i === 0)? "text-amber-400" : "text-emerald-400"} />}
              </div>
              <div className={`p-4 rounded-2xl text-[14px] shadow-sm leading-relaxed max-w-[95%] whitespace-pre-wrap ${
                  msg.role === 'user' ? 'bg-indigo-950/40 text-indigo-100 border border-indigo-800/50 rounded-tr-none' : 
                  'bg-slate-800 text-slate-200 border-l-2 rounded-tl-none ' + ((isError && i === 0) ? 'border-amber-500' : 'border-emerald-500')
              }`}>
                 {msg.content}
              </div>
           </div>
         ))}
         
         {/* Warnings if any (only show contextually at the bottom perhaps, or under first message) */}
         {warnings && warnings.length > 0 && messages.length <= 1 && warnings.map((warn, i) => (
             <div key={`warn-${i}`} className="flex gap-3">
               <div className="w-9 h-9 rounded-full bg-amber-900/50 border border-amber-500/30 flex items-center justify-center mt-1 shrink-0 shadow-[0_0_15px_rgba(245,158,11,0.2)]">
                  <ShieldAlert size={18} className="text-amber-400" />
               </div>
               <div className="bg-amber-950/20 text-amber-200 p-4 rounded-2xl rounded-tl-none text-[14px] border-l-2 border-amber-500 shadow-sm leading-relaxed max-w-[85%]">
                  <span className="font-semibold text-amber-400 pr-1">Cảnh báo Lộ trình:</span> {warn}
               </div>
            </div>
         ))}
         
      </div>

      {/* Input */}
      <div className="p-4 bg-slate-950/90 border-t border-slate-800/80 backdrop-blur-md">
         <div className="relative flex items-center">
            <input 
               type="text" 
               value={inputVal}
               onChange={(e) => setInputVal(e.target.value)}
               onKeyDown={handleKeyDown}
               placeholder="Hỏi AI hoặc yêu cầu thay đổi lộ trình..." 
               className="w-full bg-slate-900 border border-slate-700 rounded-xl text-sm pl-4 pr-12 py-3.5 text-slate-200 focus:outline-none focus:ring-1 focus:ring-emerald-500 transition-shadow shadow-inner" 
            />
            <button 
              onClick={handleSendMessage}
              className="absolute right-2 p-2 bg-emerald-500/20 text-emerald-400 rounded-lg hover:bg-emerald-500 hover:text-white transition-colors"
            >
               <Send size={18} />
            </button>
         </div>
      </div>
    </div>
  );
}
