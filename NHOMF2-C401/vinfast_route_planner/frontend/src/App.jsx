import { useState } from 'react';
import RouteMap from './components/RouteMap';
import AIAssistant from './components/AIAssistant';
import { PanelRightClose, PanelRightOpen } from 'lucide-react';

function App() {
  const [isObservationMode, setIsObservationMode] = useState(true);
  const [workflowResult, setWorkflowResult] = useState(null);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState(null);

  const handlePlanRoute = async (params) => {
    setIsLoading(true);
    setError(null);
    try {
      const response = await fetch('http://localhost:8001/api/plan', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(params),
      });
      if (!response.ok) {
        throw new Error(`API Error: ${response.status}`);
      }
      const data = await response.json();
      setWorkflowResult(data);
      if (!isObservationMode) {
        setIsObservationMode(true);
      }
    } catch (err) {
      setError(err.message);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="relative min-h-screen w-full overflow-hidden font-sans bg-slate-950">
      {/* Nền ánh sáng AI Glow */}
      <div className="absolute top-[-10%] left-[-10%] w-[40vw] h-[40vw] bg-emerald-700/15 rounded-full blur-[120px] pointer-events-none" />
      <div className="absolute top-1/2 right-0 w-[40vw] h-[50vw] bg-red-900/5 rounded-full blur-[100px] pointer-events-none" />

      {/* Nút bật tắt chế độ quan sát */}
      <button 
        onClick={() => setIsObservationMode(!isObservationMode)}
        className="absolute top-6 right-6 z-50 flex items-center gap-2 px-4 py-2 bg-slate-900/80 hover:bg-slate-800 text-emerald-400 text-sm font-medium rounded-full border border-slate-700/50 shadow-lg backdrop-blur-md transition-all"
        title="Bật/Tắt AI Dashboard"
      >
        {isObservationMode ? <PanelRightClose size={18} /> : <PanelRightOpen size={18} />}
        <span className="hidden sm:inline">AI Dashboard</span>
      </button>

      <div className="relative z-10 flex h-screen w-full p-4 lg:p-6 gap-6">
        
        {/* Phần 1: Khung trung tâm (Main View - Map & Input) */}
        <div className={`flex flex-col h-full gap-4 border border-slate-800 bg-slate-900/40 rounded-2xl shadow-2xl transition-all duration-500 ease-in-out ${
          isObservationMode ? 'w-1/2' : 'w-full max-w-5xl mx-auto'
        } overflow-hidden backdrop-blur-xl relative`}>
          <RouteMap 
            onPlanRoute={handlePlanRoute} 
            isLoading={isLoading} 
            error={error} 
            workflowResult={workflowResult} 
          />
        </div>

        {/* Phần 2: AI & Dữ liệu lộ trình (Observation Mode) */}
        <div className={`flex flex-col h-full gap-4 transition-all duration-500 ease-in-out ${
          isObservationMode ? 'w-1/2 opacity-100 translate-x-0' : 'w-0 opacity-0 translate-x-full overflow-hidden'
        }`}>
          {isObservationMode && <AIAssistant 
            workflowResult={workflowResult} 
            setWorkflowResult={setWorkflowResult}
            setIsLoading={setIsLoading}
          />}
        </div>
      </div>
    </div>
  );
}

export default App;
