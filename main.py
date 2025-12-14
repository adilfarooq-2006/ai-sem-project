
import simulation       # Flood Simulation Module
import logistics        # CSP Logistics Module (Updated)
import navigation       # Genetic Algorithm Module
from dataset import punjab_cities 

# ==========================================
# HELPER FUNCTIONS
# ==========================================
def print_header(title):
    print("\n" + "█" * 60)
    print(f"█  {title.center(54)}  █")
    print("█" * 60 + "\n")

def print_separator():
    print("-" * 60)

def prepare_data_for_logistics(active_data, priority_queue):
    flooded_list = []
    critical_city_names = [item[0] for item in priority_queue]
    for city_name in critical_city_names:
        city_data = active_data[city_name]
        logistics_entry = city_data.copy()
        logistics_entry["name"] = city_name
        if "coords" not in logistics_entry:
            logistics_entry["coords"] = [0, 0] 
        flooded_list.append(logistics_entry)
    return flooded_list

def get_critical_priority_queue(active_data):
    queue = []
    for city_name, data in active_data.items():
        if data.get('flood_status') is True or data.get('injured_count', 0) > 0:
            p_score = data.get('priority_score', 0)
            queue.append((city_name, p_score))
    queue.sort(key=lambda x: x[1], reverse=True)
    return queue

# ==========================================
# CORE LOGIC: EXECUTION
# ==========================================
def execute_rescue_operations(active_data):
    # 1. IDENTIFY TARGETS
    priority_queue = get_critical_priority_queue(active_data)

    if not priority_queue:
        print(" [STATUS] No critical zones found. Simulation needed?")
        return

    print_header("INITIALIZING RESCUE COMMAND")
    print(" [SYSTEM] Allocating Global Fleet Resources (CSP)...")
    
    # --- HIDDEN STEP: CALCULATE LOGISTICS FIRST ---
    # We do this now to reserve trucks, but we won't show the user yet.
    flooded_list = prepare_data_for_logistics(active_data, priority_queue)
    mission_logs = logistics.assign_resources(flooded_list)
    print(" [SYSTEM] Resources Allocated. Starting Missions...")

    # --- VISIBLE STEP: RESCUE MISSIONS ---
    mission_id = 1
    
    for target_city, urgency_score in priority_queue:
        print_header(f"MISSION #{mission_id}: {target_city.upper()}")
        print(f" URGENCY: {urgency_score:.2f}")

        # STEP 1: NAVIGATION (RESCUE TEAM GOES FIRST)
        start_hub = navigation.select_best_hub(target_city, active_data)
        
        if start_hub:
            print(f" [NAV] Dispatching from Hub: {start_hub}")
            print(" [NAV] Calculating Route (Genetic Algorithm)...")
            best_route = navigation.run_genetic_navigation(start_hub, target_city, active_data)
            
            if best_route:
                print(f" [NAV] 🟢 ROUTE CONFIRMED: {' -> '.join(best_route)}")
            else:
                print(f" [NAV] 🔴 FAILED: City Isolated (Roads Blocked)")
        else:
            print(" [NAV] 🔴 ERROR: No Hub Available")

        print_separator()

        # STEP 2: LOGISTICS (SUPPLIES ARRIVE AFTER ROUTE IS FOUND)
        print(" [LOGISTICS] Deploying Supply Chain...")
        
        city_log = mission_logs.get(target_city)
        
        if city_log:
            demand = city_log['total_demand']
            print(f" [LOGISTICS] Total Demand: {demand}kg")
            
            # Show the vehicles arriving
            if city_log["vehicles"]:
                for v in city_log["vehicles"]:
                    print(f"    -> 🚛 Arrived: {v['id']} | Cargo: {v['cargo']}kg")
            else:
                print("    -> ⚠️ NO VEHICLES AVAILABLE (Fleet Exhausted or Road Blocked)")
                
            remaining = city_log['remaining_demand']
            if remaining > 0:
                print(f" [STATUS] ⚠️ PARTIAL FULFILLMENT. Deficit: {remaining}kg")
            else:
                print(f" [STATUS] ✅ SUPPLY CHAIN COMPLETE.")
        
        mission_id += 1

    print("\n [INFO] All Missions Completed.")

# ==========================================
# MAIN MENU
# ==========================================
def main():
    active_data = simulation.initialize_simulation_data(punjab_cities)
    
    while True:
        print("\n" + "="*60)
        print(" AI DISASTER RESPONSE SYSTEM - COMMAND CENTER")
        print("="*60)
        print(" 1. [SIMULATION] Trigger Flood Event")
        print(" 2. [REPORT]     View Critical Priority Queue")
        print(" 3. [ACTION]     Execute Rescue Missions")
        print(" 4. [SYSTEM]     Reset Simulation Data")
        print(" 5. [SYSTEM]     Exit")
        print("="*60)
        
        choice = input("\nSelect Option [1-5]: ").strip()

        if choice == '1':
            target = input(" Enter Start City Name: ").strip().title()
            if target in active_data:
                simulation.run_flood_simulation(target, active_data)
            else:
                print(f"\n [ERROR] '{target}' not found.")

        elif choice == '2':
            queue = get_critical_priority_queue(active_data)
            print(f"\n {'CITY':<20} | {'PRIORITY':<10}")
            print("-" * 35)
            for city, score in queue:
                print(f" {city:<20} | {score:<10.2f}")

        elif choice == '3':
            execute_rescue_operations(active_data)

        elif choice == '4':
            active_data = simulation.initialize_simulation_data(punjab_cities)
            print(" [SYSTEM] Reset Complete.")

        elif choice == '5':
            break

if __name__ == "__main__":
    main()