import { useState, useEffect } from 'react';
import { MapPin, Navigation, Loader2, CheckCircle2, AlertCircle, Zap } from 'lucide-react';
import { MapContainer, TileLayer, Polyline, Marker, Popup, useMap, CircleMarker } from 'react-leaflet';
import 'leaflet/dist/leaflet.css';
import L from 'leaflet';

// Fix icon lỗi với leaflet trong react
import icon from 'leaflet/dist/images/marker-icon.png';
import iconShadow from 'leaflet/dist/images/marker-shadow.png';
let DefaultIcon = L.icon({
    iconUrl: icon,
    shadowUrl: iconShadow,
    iconSize: [25, 41],
    iconAnchor: [12, 41]
});
L.Marker.prototype.options.icon = DefaultIcon;

function BoundsUpdater({ coords }) {
  const map = useMap();
  useEffect(() => {
    if (coords && coords.length > 0) {
      const bounds = L.latLngBounds(coords);
      map.fitBounds(bounds, { padding: [50, 50] });
    }
  }, [coords, map]);
  return null;
}

export default function RouteMap({ onPlanRoute, isLoading, error, workflowResult }) {
  const [soc, setSoc] = useState(85);
  const [buffer, setBuffer] = useState(20);
  const [origin, setOrigin] = useState("Hà Nội");
  const [destination, setDestination] = useState("Vinh");
  const [stations, setStations] = useState(["Hà Nội", "Vinh"]);
  const [allMapStations, setAllMapStations] = useState([]);

  useEffect(() => {
    // Tải danh sách tên trạm cho Dropdown
    fetch('http://localhost:8001/api/stations')
      .then(r => r.json())
      .then(d => {
        if(d.stations) {
            const list = ["Hà Nội", "Vinh", "Đà Nẵng", ...d.stations];
            setStations([...new Set(list)]);
        }
      })
      .catch(e => console.error("Could not fetch stations", e));
      
    // Tải danh sách chi tiết POI (realtime preparation)
    fetch('http://localhost:8001/api/stations/all')
      .then(r => r.json())
      .then(d => {
         if(d.stations) setAllMapStations(d.stations);
      })
      .catch(e => console.error("Could not fetch POI details", e));
  }, []);

  const handleSubmit = (e) => {
    if (e) e.preventDefault();
    onPlanRoute({
      origin,
      destination,
      soc_current: parseFloat(soc),
      soc_comfort: parseFloat(buffer)
    });
  };

  // Trích xuất path từ workflowResult
  let pathCoords = [];
  let mapCenter = [19.0, 105.0]; // Default Vietnam
  const stops = workflowResult?.plan_result?.stops || [];
  
  if (workflowResult?.plan_result?.geometry) {
    pathCoords = workflowResult.plan_result.geometry.coordinates.map(c => [c[1], c[0]]);
  } else if (workflowResult?.coords) {
    const { origin: org, destination: dest } = workflowResult.coords;
    if (org) pathCoords.push([org.lat, org.lon]);
    stops.forEach(s => pathCoords.push([s.station.lat, s.station.lon]));
    if (dest) pathCoords.push([dest.lat, dest.lon]);
  }

  if (workflowResult?.coords?.origin) {
    mapCenter = [workflowResult.coords.origin.lat, workflowResult.coords.origin.lon];
  }

  // Helper để vẽ giao diện Popup
  const renderStationPopup = (st, isRouteStop = false, chargeInfo = null) => {
      return (
          <div className="flex flex-col gap-2 min-w-[240px] text-slate-800 -m-1">
              <h3 className="font-bold text-base text-slate-900 border-b pb-2 flex items-center gap-2">
                 {isRouteStop ? <Zap size={16} className="text-emerald-500 fill-emerald-500" /> : <MapPin size={16} className="text-blue-500" />}
                 {st.name}
              </h3>
              
              <div className="flex justify-between items-center text-sm pt-1">
                  <span className="text-slate-500 font-medium">Trạng thái:</span>
                  {st.status === 'active' ? (
                    <span className="flex items-center gap-1 text-emerald-600 font-semibold px-2 py-0.5 bg-emerald-100 rounded-full text-[11px] uppercase tracking-wide">
                      <CheckCircle2 size={12}/> Hoạt động
                    </span>
                  ) : (
                    <span className="flex items-center gap-1 text-amber-600 font-semibold px-2 py-0.5 bg-amber-100 rounded-full text-[11px] uppercase tracking-wide">
                      <AlertCircle size={12}/> Bảo trì
                    </span>
                  )}
              </div>
              
              <div className="flex justify-between items-center text-sm pt-1">
                  <span className="text-slate-500 font-medium">Trụ sạc {st.p_station_kw}kW:</span>
                  <span className="font-bold text-slate-900 bg-slate-100 px-2 py-0.5 rounded-lg">{st.available_slots} chỗ trống</span>
              </div>
              
              {isRouteStop && chargeInfo && (
                  <div className="mt-2 bg-emerald-50 border border-emerald-100 p-2 rounded-lg">
                      <div className="flex justify-between text-xs text-emerald-800 mb-1">
                          <span>Dự kiến đến:</span>
                          <span className="font-bold">{(chargeInfo.soc_arrive * 100).toFixed(0)}% Pin</span>
                      </div>
                      <div className="flex justify-between text-xs text-emerald-800">
                          <span>Thời gian sạc:</span>
                          <span className="font-bold">{chargeInfo.charge_min} Phút</span>
                      </div>
                  </div>
              )}
              
              {!isRouteStop && st.amenities && st.amenities.length > 0 && (
                  <div className="flex gap-1.5 flex-wrap mt-2">
                    {st.amenities.map(am => (
                      <span key={am} className="text-[10px] bg-slate-100 text-slate-500 px-2 py-1 rounded-md border border-slate-200 uppercase font-medium tracking-wider">{am}</span>
                    ))}
                  </div>
              )}
          </div>
      );
  };

  return (
    <div className="relative w-full h-full flex flex-col">
      {/* Header Panel (Input forms) nổi trên Map */}
      <div className="absolute inset-x-4 top-4 z-[1000] bg-slate-950/85 p-4 rounded-xl border border-slate-800 backdrop-blur-md shadow-[0_8px_30px_rgb(0,0,0,0.5)]">
        <form onSubmit={handleSubmit} className="flex flex-col md:flex-row items-end md:items-center gap-4">
          <div className="flex-1 flex flex-col gap-1 w-full">
            <span className="text-xs text-slate-500 font-medium tracking-wider uppercase">Điểm đi</span>
            <div className="flex items-center gap-2 bg-slate-900/50 p-1.5 rounded-lg border border-slate-800">
               <Navigation size={16} className="text-emerald-500 ml-2 shrink-0" />
               <select 
                 value={origin} 
                 onChange={e => setOrigin(e.target.value)}
                 className="w-full bg-transparent text-sm text-slate-200 outline-none p-1 appearance-none"
               >
                 {stations.map(s => <option key={`org-${s}`} value={s} className="bg-slate-900">{s}</option>)}
               </select>
            </div>
          </div>

          <div className="flex-1 flex flex-col gap-1 w-full">
            <span className="text-xs text-slate-500 font-medium tracking-wider uppercase">Điểm đến</span>
            <div className="flex items-center gap-2 bg-slate-900/50 p-1.5 rounded-lg border border-slate-800">
               <MapPin size={16} className="text-red-500 ml-2 shrink-0" />
               <select 
                 value={destination} 
                 onChange={e => setDestination(e.target.value)}
                 className="w-full bg-transparent text-sm text-slate-200 outline-none p-1 appearance-none"
               >
                 {stations.map(s => <option key={`dst-${s}`} value={s} className="bg-slate-900">{s}</option>)}
               </select>
            </div>
          </div>

          <div className="w-40 flex flex-col gap-1 shrink-0">
            <span className="text-xs text-slate-500 font-medium tracking-wider uppercase flex justify-between">
              <span>Pin hiện tại</span>
              <span className="text-emerald-400">{soc}%</span>
            </span>
            <div className="flex items-center gap-2 pt-1 h-10">
               <input 
                  type="range" min="10" max="100" value={soc} onChange={(e) => setSoc(e.target.value)}
                  className="w-full accent-emerald-500 h-1.5 bg-slate-800 rounded-lg cursor-pointer"
               />
            </div>
          </div>

          <button 
            type="submit" 
            disabled={isLoading}
            className="h-[44px] px-6 rounded-lg font-medium tracking-wide flex items-center justify-center transition-all bg-emerald-600 hover:bg-emerald-500 text-white disabled:opacity-50 shrink-0 border border-emerald-500/50"
          >
            {isLoading ? <Loader2 size={18} className="animate-spin" /> : 'Lập Lộ Trình'}
          </button>
        </form>
        {error && <div className="mt-2 text-sm text-red-400 flex gap-2"><MapPin size={16}/> {error}</div>}
      </div>

      <div className="w-full h-full bg-[#0a0f18] relative z-0">
         <MapContainer center={mapCenter} zoom={6} scrollWheelZoom={true} style={{ height: "100%", width: "100%" }}>
            <TileLayer
                url="https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}{r}.png"
                attribution='&copy; <a href="https://carto.com/attributions">CARTO</a>'
            />
            
            {/* Background Station POIs (Tất cả trạm sạc trên hệ thống) */}
            {allMapStations.map((st, idx) => {
               // Bỏ qua nếu trạm này đã có trong danh sách stops của route để không lỗi UI đè nhau
               if (stops.some(stop => stop.station.name === st.name)) return null;

               return (
                 <CircleMarker 
                   key={`poi-${idx}`} 
                   center={[st.lat, st.lon]} 
                   radius={7} 
                   pathOptions={{ 
                     color: st.status === 'active' ? '#10b981' : '#f59e0b', 
                     fillColor: '#0f172a', 
                     fillOpacity: 1, 
                     weight: 3 
                   }}
                 >
                    <Popup className="station-popup">
                       {renderStationPopup(st)}
                    </Popup>
                 </CircleMarker>
               );
            })}

            {/* Render Đường Đi (Polyline) */}
            {pathCoords.length > 0 && (
               <>
                 <Polyline positions={pathCoords} color="#10b981" weight={5} opacity={0.8} />
                 <BoundsUpdater coords={pathCoords} />
               </>
            )}

            {/* Endpoints Markers (Điểm Đầu, Điểm Cuối) */}
            {workflowResult?.coords?.origin && (
                <Marker position={[workflowResult.coords.origin.lat, workflowResult.coords.origin.lon]}>
                    <Popup>
                       <div className="font-bold text-slate-800">📍 Điểm xuất phát</div>
                       <div className="text-slate-600">{origin}</div>
                    </Popup>
                </Marker>
            )}
            {workflowResult?.coords?.destination && (
                <Marker position={[workflowResult.coords.destination.lat, workflowResult.coords.destination.lon]}>
                    <Popup>
                       <div className="font-bold text-slate-800">🏁 Điểm đến</div>
                       <div className="text-slate-600">{destination}</div>
                    </Popup>
                </Marker>
            )}

            {/* Charge Stops Markers (Các trạm trên lộ trình được AI tính toán) */}
            {stops.map((stop, idx) => (
                <Marker key={`stop-${idx}`} position={[stop.station.lat, stop.station.lon]}>
                    <Popup className="station-popup">
                       {renderStationPopup(stop.station, true, stop)}
                    </Popup>
                </Marker>
            ))}

         </MapContainer>
      </div>
    </div>
  );
}
