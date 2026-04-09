import { BatteryFull, BatteryMedium, Clock } from 'lucide-react';

export default function Timeline({ stops }) {
  if (!stops || stops.length === 0) {
     return <div className="p-4 text-center text-slate-500 text-sm">Dữ liệu hành trình liền mạch, không có điểm dừng sạc nào.</div>;
  }

  return (
    <div className="flex flex-col gap-6 pt-2 pb-4 px-2">
       {/* Các trạm sạc */}
       {stops.map((stop, idx) => (
         <div key={idx} className="relative pl-8">
            <div className="absolute w-0.5 h-full bg-slate-800 left-2 top-6" />
            <div className="absolute w-5 h-5 rounded-full bg-slate-950 border-2 border-emerald-500 left-0 top-0.5 shadow-[0_0_10px_rgba(16,185,129,0.8)] z-10 flex items-center justify-center">
               <div className="w-1.5 h-1.5 bg-emerald-500 rounded-full" />
            </div>

            <h4 className="text-slate-100 font-semibold mb-1 text-lg">{stop.station.name}</h4>
            <span className="inline-block text-xs text-slate-400 bg-slate-800/80 px-2 py-1 rounded-md mb-4 border border-slate-700/50">
              Trạm sạc {stop.station.p_station_kw}kW
            </span>

            {/* Metrics Grid */}
            <div className="grid grid-cols-3 gap-3 text-xs mb-4">
               {/* Arrive */}
               <div className="bg-slate-800/40 p-3 rounded-xl border border-slate-700/30 flex flex-col items-center justify-center gap-1">
                 <BatteryMedium size={18} className="text-amber-400 mb-1" />
                 <span className="text-slate-400">Đến nơi</span>
                 <span className="text-amber-400 font-bold text-xl">{(stop.soc_arrive * 100).toFixed(0)}%</span>
               </div>
               
               {/* Charge */}
               <div className="bg-slate-800/40 p-3 rounded-xl border border-slate-700/30 flex flex-col items-center justify-center gap-1 relative overflow-hidden">
                 <div className="absolute bottom-0 left-0 w-full h-[2px] bg-emerald-500/50" />
                 <Clock size={18} className="text-slate-200 mb-1" />
                 <span className="text-slate-400">Sạc pin</span>
                 <span className="text-white font-bold text-xl">{stop.charge_min}m</span>
               </div>
               
               {/* Depart */}
               <div className="bg-slate-800/40 p-3 rounded-xl border border-slate-700/30 flex flex-col items-center justify-center gap-1">
                 <BatteryFull size={18} className="text-emerald-400 mb-1" />
                 <span className="text-slate-400">Rời đi</span>
                 <span className="text-emerald-400 font-bold text-xl">{(stop.soc_depart * 100).toFixed(0)}%</span>
               </div>
            </div>
         </div>
       ))}
    </div>
  );
}
