import simulation  # Flood Simulation Module
import logistics  # CSP Logistics Module (Swarm Updated)
import navigation  # Genetic Algorithm / Aerial Module
import visualization  # Map Generation
from dataset import punjab_cities


# ==========================================
# HELPER FUNCTIONS
# ==========================================

def get_critical_priority_queue(active_data):
    queue = []
    for city_name, data in active_data.items():
        if data.get('flood_status') is True or data.get('injured_count', 0) > 0:
            p_score = data.get('priority_score', 0)
            queue.append((city_name, p_score))
    queue.sort(key=lambda x: x[1], reverse=True)
    return queue


def prepare_single_city_for_logistics(city_name, active_data):
    city_data = active_data[city_name]
    logistics_entry = city_data.copy()
    logistics_entry["name"] = city_name
    if "coords" not in logistics_entry:
        logistics_entry["coords"] = (31.5204, 74.3587)  # Fallback to Lahore coords
    return [logistics_entry]


# ==========================================
# CORE LOGIC: HYBRID EXECUTION
# ==========================================

def execute_rescue_operations(active_data):
    priority_queue = get_critical_priority_queue(active_data)

    if not priority_queue:
        print("[STATUS]: No critical zones found. Please run Simulation first.")
        return

    print("\n[SYSTEM]: INITIALIZING HYBRID RESCUE COMMAND...")
    print(f"[SYSTEM]: {len(priority_queue)} Critical Zones Identified.")
    print("=" * 60)

    mission_id = 1

    for target_city, urgency_score in priority_queue:
        print(f"\nMISSION #{mission_id}: {target_city.upper()}")
        print("-" * 40)

        # 1. SELECT HUB
        start_hub = navigation.select_best_hub(target_city, active_data)
        if not start_hub:
            print("[ERROR]: No start hub found.")
            continue

        # 2. HYBRID NAVIGATION LOGIC (The Fix)
        # Check road status to decide if we fly (Direct) or drive (GA)
        road_status = active_data[target_city].get('road_status', 'Open')
        best_route = None

        if road_status == "Blocked":
            # AIR LOGIC: Point-to-Point displacement (Haversine Path)
            print(f"[NAV]: Road Blocked. Aerial Mission Confirmed.")
            print(f"[NAV]: Bypassing road network for direct flight to {target_city}...")
            # We simply return the start and end city as the "path"
            best_route = [start_hub, target_city]
        else:
            # GROUND LOGIC: Must navigate open roads using GA
            print(f"[NAV]: Road Open. Ground Mission via Genetic Algorithm...")
            best_route = navigation.run_genetic_navigation(start_hub, target_city, active_data)

        if best_route:
            print(f"[NAV] ROUTE CONFIRMED: {' -> '.join(best_route)}")
        else:
            print(f"[NAV] FAILED: Target Isolated")

        print("-" * 40)

        # 3. LOGISTICS (Deliver Supplies - Swarm Updated)
        formatted_city_list = prepare_single_city_for_logistics(target_city, active_data)
        mission_assignments = logistics.assign_resources(formatted_city_list)

        # 4. VISUALIZATION (Generate Map with dynamic colors)
        if best_route:
            print("[VISUALIZATION] Generating Mission Map...")
            visualization.generate_mission_map(
                active_data,
                path=best_route,
                assignments=mission_assignments,
                filename=f"mission_{target_city}.html"
            )

        print("=" * 60)
        mission_id += 1

    print("\n[INFO] All Hybrid Missions Completed.")


# ==========================================
# MAIN MENU
# ==========================================
def main():
    active_data = simulation.initialize_simulation_data(punjab_cities)
    while True:
        print("\n" + "=" * 60)
        print(" AI DISASTER RESPONSE SYSTEM - COMMAND CENTER")
        print("=" * 60)
        print(" 1. [SIMULATION] Trigger Flood Event")
        print(" 2. [REPORT]     View Critical Priority Queue")
        print(" 3. [ACTION]     Execute Rescue Missions")
        print(" 4. [SYSTEM]     Reset Simulation Data")
        print(" 5. [SYSTEM]     Exit")
        print("=" * 60)

        choice = input("\nSelect Option [1-5]: ").strip()
        if choice == '1':
            target = input("Enter Start City Name: ").strip().title()
            if target in active_data:
                simulation.run_flood_simulation(target, active_data)
            else:
                print(f"[ERROR]: '{target}' not found.")
        elif choice == '2':
            queue = get_critical_priority_queue(active_data)
            if not queue:
                print("\n[INFO]: No active alerts.")
            else:
                print(f"\n {'CITY':<20} | {'PRIORITY':<10} | {'ROAD STATUS':<12}")
                print("-" * 50)
                for city, score in queue:
                    status = active_data[city].get('road_status', 'Unknown')
                    print(f" {city:<20} | {score:<10} | {status:<12}")
        elif choice == '3':
            execute_rescue_operations(active_data)
        elif choice == '4':
            active_data = simulation.initialize_simulation_data(punjab_cities)
            print("[SYSTEM]: Data Reset.")
        elif choice == '5':
            break
        else:
            print("Invalid Selection.")


if __name__ == "__main__":
    main()