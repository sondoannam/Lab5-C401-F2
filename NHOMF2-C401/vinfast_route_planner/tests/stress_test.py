import time
import random
import sys
import os
from typing import List, Dict, Any

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from core.route_planner import plan_route

def generate_mock_stations(num_stations: int) -> List[Dict[str, Any]]:
    stations: List[Dict[str, Any]] = []
    curr_lat: float = 10.0
    curr_lon: float = 106.0
    
    for i in range(num_stations):
        curr_lat += random.uniform(0.01, 0.05)
        curr_lon += random.uniform(0.01, 0.05)
        
        status: str = "active" if random.random() > 0.05 else "maintenance"
        p_station: float = random.choice([50.0, 60.0, 150.0, 250.0])
        
        stations.append({
            "id": f"ST_{i}",
            "name": f"VinFast Stress Station {i}",
            "lat": curr_lat,
            "lon": curr_lon,
            "status": status,
            "p_station_kw": p_station
        })
        
    return stations

def run_stress_test(num_stations: int = 50000) -> None:
    print(f"Khởi tạo {num_stations} trạm giả lập...")
    start_gen: float = time.time()
    stations: List[Dict[str, Any]] = generate_mock_stations(num_stations)
    end_gen: float = time.time()
    print(f"Hoàn tất khởi tạo trong {end_gen - start_gen:.4f} giây.\n")
    
    origin: Tuple[float, float] = (10.0, 106.0)
    
    last_station: Dict[str, Any] = stations[-1]
    destination: Tuple[float, float] = (float(last_station["lat"]) + 0.1, float(last_station["lon"]) + 0.1)
    
    print(f"Bắt đầu định tuyến từ trạm 0 đến trạm {num_stations-1} (-{num_stations * 7.5:,.0f} km)...")
    
    start_routing: float = time.time()
    result: Dict[str, Any] = plan_route(origin, destination, 0.90, stations)
    end_routing: float = time.time()
    
    duration: float = end_routing - start_routing
    
    print("\n--- KẾT QUẢ STRESS TEST ---")
    print(f"Trạng thái khả thi (Feasible): {result['feasible']}")
    print(f"Tổng số lần dừng sạc: {len(result['stops'])} lần")
    print(f"Tổng thời gian sạc ước tính: {result['total_time_min']:.2f} phút")
    print(f"Thời gian tính toán thuật toán: {duration:.4f} giây")
    print("----------------------------\n")

if __name__ == "__main__":
    run_stress_test(50000)
