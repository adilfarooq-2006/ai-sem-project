
import simulation       # Flood Simulation Module
import logistics        # CSP Logistics Module (Updated)
import navigation       # Genetic Algorithm Module
from dataset import punjab_cities 

# ==========================================
# HELPER FUNCTIONS
# ==========================================

def get_critical_priority_queue(active_data):
    """
    Returns a list of tuples: (city_name, priority_score)
    Sorted by urgency (highest first).
    """
    queue = []
    for city_name, data in active_data.items():
        # Filter for cities that are flooded OR have injuries
        if data.get('flood_status') is True or data.get('injured_count', 0) > 0:
            p_score = data.get('priority_score', 0)
            queue.append((city_name, p_score))
            
    # Sort descending by score
    queue.sort(key=lambda x: x[1], reverse=True)
    return queue

def prepare_single_city_for_logistics(city_name, active_data):
    """
    Formats a single city's data into a list containing one dictionary,
    matching the input format expected by logistics.assign_resources()
    """
    city_data = active_data[city_name]
    logistics_entry = city_data.copy()
    logistics_entry["name"] = city_name
    
    # Ensure coords exist (fallback if missing)
    if "coords" not in logistics_entry:
        logistics_entry["coords"] = (0, 0)
        
    # Return as a list because assign_resources expects a list
    return [logistics_entry]

# ==========================================
# CORE LOGIC: EXECUTION
# ==========================================
def execute_rescue_operations(active_data):
    # 1. IDENTIFY TARGETS
    priority_queue = get_critical_priority_queue(active_data)

    if not priority_queue:
        print("[STATUS]: No critical zones found. Please run the Flood Simulation first (Option 1).")
        return

    print("\n[SYSTEM]: INITIALIZING RESCUE COMMAND...")
    print(f"[SYSTEM]: {len(priority_queue)} Critical Zones Identified.")
    print("[SYSTEM]: Starting Sequential Missions...")
    print("="*60)

    mission_id = 1
    
    # EXECUTE SEQUENTIAL MISSIONS
    for target_city, urgency_score in priority_queue:

        print(f"\nMISSION #{mission_id}: {target_city.upper()}")
        print(f" URGENCY SCORE: {urgency_score}")
        print("-" * 40)

        # ----------------------------------------
        # PHASE A: NAVIGATION (Find the Path)
        # ----------------------------------------
        start_hub = navigation.select_best_hub(target_city, active_data)
        
        if start_hub:
            print(f"[NAV]: Calculating Route (Genetic Algorithm)...")
            
            # Run GA
            best_route = navigation.run_genetic_navigation(
                start_hub, 
                target_city, 
                active_data, 
            )
            
            if best_route:
                print("[NAV]: ROUTE FOUND!")
                path_str = " -> ".join(best_route)
                print(f"[NAV]: Best Route out of 100 generations: {path_str}")
            else:
                print(f"[ERROR]: NO ROUTE FOUND!")
        else:
            print("[ERROR]: No Hub Available (Check dataset)")

        print("-" * 40)

        # ----------------------------------------
        # PHASE B: LOGISTICS (Deliver Supplies)
        # ----------------------------------------
        # We invoke the Logistics module directly here.
        # It will calculate needs and PRINT the vehicle assignments immediately.
        
        formatted_city_list = prepare_single_city_for_logistics(target_city, active_data)
        
        # This function prints its own output (No return value used)
        logistics.assign_resources(formatted_city_list)
        
        print("="*60)
        mission_id += 1

    print("\n[INFO] All Missions Completed.")

# ==========================================
# MAIN MENU
# ==========================================
def main():
    # Load Initial Data
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
            target = input("Enter Start City Name (e.g. Lahore, Sialkot, Rawalpindi): ").strip().title()
            if target in active_data:
                simulation.run_flood_simulation(target, active_data)
            else:
                print(f"\n[ERROR]: '{target}' not found in dataset.")

        elif choice == '2':
            queue = get_critical_priority_queue(active_data)

            if not queue:
                print("\n[INFO]: No active alerts. Run simulation first.")
            else:
                # 1. Update Header to include Road Status
                print(f"\n {'CITY':<20} | {'PRIORITY':<10} | {'ROAD STATUS':<12}")
                print("-" * 50)
                
                for city, score in queue:
                    # 2. Retrieve status from the main dataset
                    status = active_data[city].get('road_status', 'Unknown')
                    
                    # 3. Print with alignment
                    print(f" {city:<20} | {score:<10} | {status:<12}")

        elif choice == '3':
            execute_rescue_operations(active_data)

        elif choice == '4':
            active_data = simulation.initialize_simulation_data(punjab_cities)
            print("[SYSTEM]: Simulation Data Reset.")

        elif choice == '5':
            print("[SYSTEM]: Shutting down...")
            break
        
        else:
            print("Invalid Selection.")

if __name__ == "__main__":
    main()