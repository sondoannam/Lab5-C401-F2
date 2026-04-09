import math
import unittest
from typing import Any, Dict, List, Tuple, Optional

def get_distance_km(coord1: Tuple[float, float], coord2: Tuple[float, float]) -> float:
    lat1, lon1 = coord1
    lat2, lon2 = coord2
    radius = 6371.0
    dlat = math.radians(lat2 - lat1)
    dlon = math.radians(lon2 - lon1)
    a = math.sin(dlat / 2)**2 + math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) * math.sin(dlon / 2)**2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    return radius * c

def calculate_charging_stats(soc_arrive: float, soc_target: float, p_station_kw: float, battery_capacity: float = 82.0, p_vehicle_kw: float = 150.0) -> Tuple[float, float]:
    if soc_arrive >= soc_target:
        return round(float(soc_arrive), 4), 0.0
    
    p_effective: float = min(p_vehicle_kw, p_station_kw)
    energy_needed: float = (soc_target - soc_arrive) * battery_capacity
    charge_time_hours: float = energy_needed / p_effective
    charge_min: float = charge_time_hours * 60.0
    
    return round(float(soc_target), 4), round(charge_min, 4)

def plan_route(origin_coord: Tuple[float, float], destination_coord: Tuple[float, float], soc_current: float, stations: List[Dict[str, Any]], soc_comfort: float = 0.20) -> Dict[str, Any]:
    soc_hard: float = 0.10
    battery_capacity: float = 82.0
    energy_consumption: float = 0.22
    soc_target: float = 0.80
    
    stops: List[Dict[str, Any]] = []
    warnings: List[str] = []
    feasible: bool = True
    total_time_min: float = 0.0
    
    current_pos: Tuple[float, float] = origin_coord
    current_soc: float = float(soc_current)
    active_stations: List[Dict[str, Any]] = [s for s in stations if s.get("status") == "active"]
    station_index: int = 0
    
    while True:
        dist_to_dest: float = get_distance_km(current_pos, destination_coord)
        soc_at_dest: float = current_soc - (energy_consumption * dist_to_dest) / battery_capacity
        
        if soc_at_dest >= soc_hard:
            if soc_at_dest < soc_comfort:
                warnings.append("SoC thấp tại chặng đến Điểm đích")
            break
            
        best_station: Optional[Dict[str, Any]] = None
        best_index: int = -1
        best_soc_arrive: float = 0.0
        
        for i in range(station_index, len(active_stations)):
            station: Dict[str, Any] = active_stations[i]
            station_coord: Tuple[float, float] = (float(station["lat"]), float(station["lon"]))
            dist: float = get_distance_km(current_pos, station_coord)
            soc_arrive: float = current_soc - (energy_consumption * dist) / battery_capacity
            
            if soc_arrive >= soc_hard:
                best_station = station
                best_index = i
                best_soc_arrive = soc_arrive
                
        if best_station is None:
            feasible = False
            break
            
        if best_soc_arrive < soc_comfort:
            warnings.append(f"SoC thấp tại chặng đến {best_station['name']}")
            
        p_station_kw: float = float(best_station.get("p_station_kw", 50.0))
        soc_depart, charge_min = calculate_charging_stats(best_soc_arrive, soc_target, p_station_kw, battery_capacity)
        
        total_time_min += charge_min
            
        stops.append({
            "station": best_station,
            "soc_arrive": round(float(best_soc_arrive), 4),
            "charge_min": charge_min,
            "soc_depart": soc_depart
        })
        
        current_pos = (float(best_station["lat"]), float(best_station["lon"]))
        current_soc = soc_depart
        station_index = best_index + 1
        
    return {
        "stops": stops,
        "total_time_min": round(total_time_min, 4),
        "feasible": feasible,
        "warnings": warnings,
        "soc_hard": soc_hard,
        "soc_comfort": soc_comfort
    }

class TestRoutePlanner(unittest.TestCase):
    def setUp(self) -> None:
        self.origin: Tuple[float, float] = (21.0285, 105.8542)
        self.destination: Tuple[float, float] = (16.0471, 108.2068)
        self.stations: List[Dict[str, Any]] = [
            {"id": "ST_01", "name": "VinFast Thanh Hoa", "lat": 19.8075, "lon": 105.7764, "status": "active", "p_station_kw": 250},
            {"id": "ST_02", "name": "VinFast Vinh", "lat": 18.6796, "lon": 105.6813, "status": "active", "p_station_kw": 60},
            {"id": "ST_03", "name": "VinFast Ha Tinh", "lat": 18.3333, "lon": 105.9000, "status": "maintenance", "p_station_kw": 250},
            {"id": "ST_04", "name": "VinFast Dong Hoi", "lat": 17.4833, "lon": 106.6000, "status": "active", "p_station_kw": 150},
            {"id": "ST_05", "name": "VinFast Hue", "lat": 16.4637, "lon": 107.5909, "status": "active", "p_station_kw": 11}
        ]
        
    def test_calculate_charging_stats(self) -> None:
        soc_depart, charge_min = calculate_charging_stats(0.20, 0.80, 60.0)
        self.assertEqual(soc_depart, 0.80)
        self.assertAlmostEqual(charge_min, 49.2, places=2)
        
    def test_feasible_route(self) -> None:
        result = plan_route(self.origin, self.destination, 0.85, self.stations)
        self.assertTrue(result["feasible"])
        self.assertIsInstance(result["stops"], list)
        self.assertIn("soc_hard", result)
        self.assertGreater(result["total_time_min"], 0.0)
        
    def test_unfeasible_route(self) -> None:
        result = plan_route(self.origin, self.destination, 0.15, self.stations)
        self.assertFalse(result["feasible"])

if __name__ == "__main__":
    unittest.main(argv=[''], exit=False)
