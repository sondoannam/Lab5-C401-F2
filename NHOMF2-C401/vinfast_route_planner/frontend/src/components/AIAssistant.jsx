import { Sparkles } from 'lucide-react';
import Timeline from './Timeline';
import ChatbotUI from './ChatbotUI';

export default function AIAssistant({ workflowResult, setWorkflowResult, setIsLoading }) {
  const result = workflowResult?.plan_result;
  const stops = result?.stops || [];
  
  return (
    <div className={`flex-1 flex flex-col h-full bg-slate-900 ${workflowResult ? 'border-l border-slate-800 shadow-2xl relative p-4 gap-4' : 'items-stretch p-4 gap-4 glow-wrapper'} overflow-hidden`}>
      {!workflowResult ? (
        <div className="flex-1 flex flex-col items-center justify-center bg-slate-900/60 rounded-2xl border border-slate-700/50 backdrop-blur-xl shrink-0 p-8 min-h-[30%]">
            <Sparkles size={32} className="text-slate-600 mb-4" />
            <p className="text-slate-400 text-center text-sm">Hãy chọn điểm đi và điểm đến, hoặc chat trực tiếp với AI để vạch ra chiến lược sạc tối ưu nhất.</p>
        </div>
      ) : (
        <>
          {/* AI Strategy Banner */}
          <div className="p-4 rounded-xl bg-gradient-to-r from-emerald-900/40 to-slate-900 border border-emerald-800/50 shadow-[0_0_20px_rgba(16,185,129,0.1)] relative overflow-hidden shrink-0">
             <div className="absolute top-0 right-0 w-32 h-32 bg-emerald-500/10 blur-3xl rounded-full" />
             
             <div className="flex items-center gap-2 mb-3 relative z-10">
                <div className="bg-emerald-500/20 p-1.5 rounded-lg border border-emerald-500/30">
                   <Sparkles size={16} className="text-emerald-400" />
                </div>
                <span className="text-emerald-400 text-xs font-bold uppercase tracking-widest">Trợ lý Lộ trình</span>
             </div>
             <div className="text-slate-200 text-sm font-medium leading-relaxed tracking-wide relative z-10">
               {stops.length > 0 ? (
                   <>
                     Trạm sạc dự kiến: <span className="text-emerald-400 font-bold">{stops.length} lần</span>, 
                     tổng thời gian đi: <span className="text-white font-semibold">{result.total_time_min} phút</span>.
                   </>
               ) : (
                 <span className="text-emerald-400 font-bold">Không cần sạc giữa đường! Đi một mạch tới đích.</span>
               )}
             </div>
          </div>
          
          {/* Timeline Section */}
          <div className="overflow-y-auto pr-2 scrollbar-thin scrollbar-thumb-slate-800 scrollbar-track-transparent max-h-[35%] shrink-0">
             <Timeline stops={stops} />
          </div>
        </>
      )}

      {/* AI Chatbot Module */}
      <ChatbotUI 
        summary={workflowResult?.summary_text} 
        warnings={result?.warnings} 
        feasible={result?.feasible} 
        setWorkflowResult={setWorkflowResult}
        setIsLoading={setIsLoading}
      />
    </div>
  );
}
