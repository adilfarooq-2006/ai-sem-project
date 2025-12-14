import math
import simulation      # Flood Simulation Module
import navigation      # Genetic Algorithm Module
from dataset import punjab_cities  # Citites Data



# ==========================================
# 2. PRIORITY QUEUE LOGIC
# ==========================================
def get_critical_priority_queue(active_data):
    """
    Scans the simulation data and returns a list of cities 
    sorted by Urgency (Highest Priority Score first).
    """
    queue = []
    
    for city_name, data in active_data.items():
        # Filter: Only include cities that actually need help
        # (Must be flooded OR have injuries)
        if data.get('flood_status') is True or data.get('injured_count', 0) > 0:
            p_score = data.get('priority_score', 0)
            queue.append((city_name, p_score))
    
    # Sort the list: High score (index 1) at the top
    queue.sort(key=lambda x: x[1], reverse=True)
    
    return queue

# ==========================================
# 3. MAIN CONTROLLER
# ==========================================
def main():
    print("==========================================")
    print("   AI DISASTER RESPONSE: PRIORITY ENGINE  ")
    print("==========================================\n")

    # --- STEP 1: INITIALIZE & SIMULATE ---
    active_data = simulation.initialize_simulation_data(punjab_cities)
    
    flood_source = "Sialkot" # Example source
    print(f"[SIMULATION] Running flood surge starting from {flood_source}...")
    simulation.run_flood_simulation(flood_source, active_data)
    
    # --- STEP 2: GENERATE PRIORITY QUEUE ---
    # This replaces the manual user input
    priority_queue = get_critical_priority_queue(active_data)
    
    if not priority_queue:
        print("[STATUS] No critical cities found. System Standby.")
        return

    print(f"\n[ALERT] {len(priority_queue)} Critical Zones Identified.")
    print(f"Critical Areas\n: {[x[0] for x in priority_queue]}...")
    
    print("\n" + "="*40)
    print("        STARTING RELIEF OPERATIONS")
    print("="*40)

    # --- STEP 3: MISSION LOOP (Serve until empty) ---
    mission_id = 1
    
    while priority_queue:
        # Pop the most critical city from the top
        target_city, urgency_score = priority_queue.pop(0)
        
        print(f"\n>>> MISSION #{mission_id}: TARGETING {target_city}")
        print(f"    URGENCY SCORE: {urgency_score:.2f}")
        
        # 3a. Select Logistics Hub
        start_hub = navigation.select_best_hub(target_city, active_data)
        if not start_hub:
            print("    [ERROR] No Hub available. Skipping.")
            continue
            
        print(f"    DISPATCHING FROM: {start_hub}")
        
        # 3b. Run GA Navigation
        print("    [AI] Computing optimal route...")
        best_route = navigation.run_genetic_navigation(
            start=start_hub, 
            end=target_city, 
            graph_data=active_data,
        )
        
        # 3c. Output Result
        if best_route:
            print(f"    [SUCCESS] Route Confirmed: {' -> '.join(best_route)}")
        else:
            print(f"    [FAILED] No path found. City isolated.")
            
        print("    " + "-"*30)
        mission_id += 1
        # Optional: Add small delay to make output readable
        # time.sleep(0.5) 

    print("\n" + "="*40)
    print("ALL TARGETS PROCESSED. QUEUE EMPTY.")
    print("="*40)

if __name__ == "__main__":
    main()