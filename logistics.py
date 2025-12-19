# helper function to calculate cargo weight based purely on injured count.
def calculateDemand(flooded_city_data):
    injured_count = flooded_city_data.get("injured_count", 0)
    SUPPLY_PER_PERSON = 2
    needed_weight = injured_count * SUPPLY_PER_PERSON

    return {
        "city_name": flooded_city_data["name"],
        "injured_count": injured_count,
        "needed_weight": needed_weight,
        "road_status": flooded_city_data["road_status"],
        "location": flooded_city_data["coords"]
    }

def initializeFleet():
    fleet = []
    # 50 Trucks - Capacity 3000kg
    for i in range(1, 51):
        fleet.append({"id": f"Truck-{i}", "type": "truck", "capacity": 3000, "speed": "slow", "available": True})
    # 50 Drones - Capacity 50kg (Total Swarm Capacity: 2500kg)
    for i in range(1, 51):
        fleet.append({"id": f"Drone-{i}", "type": "drone", "capacity": 50, "speed": "fast", "available": True})
    # 10 Helis - Capacity 25000kg
    for i in range(1, 11):
        fleet.append({"id": f"Helicopter-{i}", "type": "heli", "capacity": 25000, "speed": "fast", "available": True})
    return fleet

def check_valid_for_split_delivery(vehicle, city_demand):
    isTruck = vehicle.get("type") in ["truck", "emergency_truck"]
    roadBlocked = city_demand.get("road_status") == "Blocked"
    # Trucks cannot travel on blocked roads
    return not (isTruck and roadBlocked)

def get_prioritized_fleet(fleet, city_demand):
    road_status = city_demand["road_status"]
    needed_weight = city_demand["needed_weight"]
    available_vehicles = [v for v in fleet if v["available"]]

    # Define your threshold
    SWARM_LIMIT = 2500

    def sort_key(vehicle):
        v_type = vehicle["type"]

        # IF ROADS ARE BLOCKED: Decide based on weight threshold
        if road_status == "Blocked":
            if needed_weight > SWARM_LIMIT:
                # Priority: Heli -> Drone (Heli is first choice for heavy loads)
                return 1 if v_type == "heli" else 2 if v_type == "drone" else 999
            else:
                # Priority: Drone -> Heli (Drones are first choice for lighter loads)
                return 1 if v_type == "drone" else 2 if v_type == "heli" else 999

        # IF ROADS ARE OPEN: Trucks are always priority #1
        else:
            if v_type == "truck": return 1
            if v_type == "emergency_truck": return 2
            # For open roads, if trucks are busy, air support follows the same weight rule
            if needed_weight > SWARM_LIMIT:
                return 3 if v_type == "heli" else 4 if v_type == "drone" else 999
            else:
                return 3 if v_type == "drone" else 4 if v_type == "heli" else 999

    return sorted(available_vehicles, key=sort_key)

def create_emergency_vehicle(idx, is_air_support=False):
    # Fallback if the initial fleet is exhausted
    if is_air_support:
        return {"id": f"AirLift-{idx}", "type": "heli", "capacity": 50000, "speed": "fast", "available": True}
    return {"id": f"Rental-Truck-{idx}", "type": "emergency_truck", "capacity": 5000, "speed": "slow", "available": True}

def assign_resources(flooded_cities_list):
    fleet = initializeFleet()
    emergency_counter = 1
    all_mission_assignments = []

    priority_queue = sorted(
        [calculateDemand(c) for c in flooded_cities_list],
        key=lambda x: x['injured_count'],
        reverse=True
    )

    for city in priority_queue:
        assigned_vehicles_log = []
        needed_weight = city["needed_weight"]
        candidate_vehicles = get_prioritized_fleet(fleet, city)

        # Greedy fill loop
        for vehicle in candidate_vehicles:
            if needed_weight <= 0: break
            if check_valid_for_split_delivery(vehicle, city):
                vehicle["available"] = False
                delivered = min(needed_weight, vehicle["capacity"])
                needed_weight -= delivered
                assigned_vehicles_log.append(f"{vehicle['id']} ({delivered}kg)")

        # If fleet is empty but demand remains, create emergency vehicles
        while needed_weight > 0:
            road_blocked = city["road_status"] == "Blocked"
            ev = create_emergency_vehicle(emergency_counter, is_air_support=road_blocked)
            emergency_counter += 1
            delivered = min(needed_weight, ev["capacity"])
            needed_weight -= delivered
            
            assigned_vehicles_log.append(f"EMERGENCY: {emergency_vehicle['id']} ({delivered}kg)")

        all_mission_assignments.extend(assigned_vehicles_log)
        print(f"CITY: {city['city_name'].upper()} | Status: Fulfilled | Assigned: {', '.join(assigned_vehicles_log)}")

    return all_mission_assignments