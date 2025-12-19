import simulation  # Flood Simulation Module
import logistics  # CSP Logistics Module (Swarm & Weight Threshold)
import navigation  # Genetic Algorithm / Aerial Module
import visualization  # Map Generation
from dataset import punjab_cities


# =========================================
# PROLOG-STYLE LOGIC ENGINE (XAI)
# =========================================
class DisasterLogicEngine:
    def __init__(self):
        # High-level "Knowledge Base" Facts
        self.SWARM_THRESHOLD = 2500  # Heli vs Drone limit

    def get_xai_log(self, vehicle, weight, road_status, distance):
        """
        Mimics Prolog's Traceability. Explains WHY a vehicle was chosen.
        """
        # Data Normalization for the Log
        facts = f"Facts: Weight={weight}kg, Road={road_status}, Dist={round(distance, 1)}km"

        if road_status == "Blocked":
            if weight > self.SWARM_THRESHOLD:
                reason = f"Decision: HELICOPTER. Logic: weight({weight}) > limit({self.SWARM_THRESHOLD}) AND road(Blocked). Rule 'Heavy_Lift_Protocol' triggered."
            else:
                reason = f"Decision: DRONE SWARM. Logic: weight({weight}) <= limit({self.SWARM_THRESHOLD}) AND road(Blocked). Rule 'Aerial_Swarm_Efficiency' triggered."
        else:
            reason = f"Decision: TRUCK CONVOY. Logic: road(Open). Rule 'Ground_Priority' triggered. Ground travel is most cost-effective."

        return f"\n[XAI REASONING LOG]\n{facts}\n{reason}"


# Create the global engine instance
logic_engine = DisasterLogicEngine()


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
    return [logistics_entry]


# ==========================================
# CORE LOGIC: HYBRID EXECUTION WITH XAI
# ==========================================

def execute_rescue_operations(active_data):
    priority_queue = get_critical_priority_queue(active_data)

    if not priority_queue:
        print("[STATUS]: No critical zones found. Please run Simulation first.")
        return

    print("\n[SYSTEM]: INITIALIZING HYBRID RESCUE COMMAND (XAI ENABLED)...")
    print(f"[SYSTEM]: {len(priority_queue)} Missions queued.")
    print("=" * 60)

    for mission_id, (target_city, urgency_score) in enumerate(priority_queue, 1):
        print(f"\nMISSION #{mission_id}: {target_city.upper()}")
        print("-" * 40)

        # 1. SELECT HUB
        start_hub = navigation.select_best_hub(target_city, active_data)

        # 2. HYBRID NAVIGATION LOGIC
        road_status = active_data[target_city].get('road_status', 'Open')
        best_route = None

        if road_status == "Blocked":
            print(f"[NAV]: Road Blocked. Aerial Mission Confirmed.")
            best_route = [start_hub, target_city]
        else:
            print(f"[NAV]: Road Open. Ground Mission via Genetic Algorithm...")
            best_route = navigation.run_genetic_navigation(start_hub, target_city, active_data)

        # 3. LOGISTICS (Deliver Supplies)
        formatted_city_list = prepare_single_city_for_logistics(target_city, active_data)
        mission_assignments = logistics.assign_resources(formatted_city_list)

        # --- XAI LOGIC: SYNC WEIGHT DATA ---
        # We extract the weight that was actually assigned to the vehicles
        total_weight = 0
        lead_vehicle = "truck"

        for assignment in mission_assignments:
            if "Helicopter" in assignment:
                lead_vehicle = "heli"
            elif "Drone" in assignment:
                lead_vehicle = "drone"

            # Extract number between '(' and 'kg)'
            if '(' in assignment and 'kg' in assignment:
                try:
                    w_val = assignment.split('(')[1].split('kg')[0]
                    total_weight += int(w_val)
                except:
                    pass

        dist = navigation.calculate_distance(start_hub, target_city, active_data)
        reasoning = logic_engine.get_xai_log(lead_vehicle, total_weight, road_status, dist)

        # # Output results to console
        # print(f"CITY: {target_city} | Status: Fulfilled")
        # print(f"Assigned: {', '.join(mission_assignments)}")
        print(reasoning)
        # -----------------------------------

        # 4. VISUALIZATION
        if best_route:
            print(f"[VISUALIZATION] Generating Mission Map...")
            visualization.generate_mission_map(
                active_data,
                path=best_route,
                assignments=mission_assignments,
                filename=f"mission_{target_city}.html"
            )

        print("=" * 60)

        # We assume active_data structure holds the urgency. 
        # By setting it to 0, it is no longer "Critical".
        if target_city in active_data:
            active_data[target_city]['urgency'] = 0 
            active_data[target_city]['status'] = 'Safe' # Optional flag
            active_data[target_city]['injured_count'] = 0
            # ==========================================================

    print("=" * 60)
    print("\n[INFO] All Hybrid Missions Completed. Queue reset.")
    print("[INFO] Active Data updated: Critical zones marked as Safe.")
    


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
        print(" 2. [REPORT]     View Priority Queue")
        print(" 3. [ACTION]     Execute Missions (Hybrid + XAI)")
        print(" 4. [SYSTEM]     Reset Data")
        print(" 5. [SYSTEM]     Exit")
        print("=" * 60)

        choice = input("\nSelect Option [1-5]: ").strip()
        if choice == '1':
            target = input("Enter Start City: ").strip().title()
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
                    print(f" {city:<20} | {score:<10.2f} | {status}")
        elif choice == '3':
            execute_rescue_operations(active_data)
        elif choice == '4':
            active_data = simulation.initialize_simulation_data(punjab_cities)
            print("[SYSTEM]: Simulation Data Reset.")
        elif choice == '5':
            print("[SYSTEM]: Shutting down Command Center. Goodbye.")
            break


if __name__ == "__main__":
    main()