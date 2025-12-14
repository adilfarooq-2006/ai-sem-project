# helper function to calculate cargo weight based purely on injured count.
def calculateDemand(flooded_city_data):
    injured_count = flooded_city_data.get("injured_count", 0)
    SUPPLY_PER_PERSON = 5
    needed_weight = injured_count * SUPPLY_PER_PERSON

    return {
        "city_name": flooded_city_data["name"],
        "injured_count": injured_count,
        "needed_weight": needed_weight,
        "road_status": flooded_city_data["road_status"],
        "location": flooded_city_data["coords"]
    }

# vehicle resourses
def initializeFleet():
    fleet = []
    # 50 Trucks
    for i in range(1, 51):
        fleet.append({"id": f"Truck-{i}", "type": "truck", "capacity": 3000, "speed": "slow", "available": True})
    # 100 Drones
    for i in range(1, 101):
        fleet.append({"id": f"Drone-{i}", "type": "drone", "capacity": 50, "speed": "fast", "available": True})
    # 10 Helis
    for i in range(1, 11):
        fleet.append({"id": f"Helicopter-{i}", "type": "heli", "capacity": 25000, "speed": "fast", "available": True})
    return fleet

# Constraints CSP
def check_valid_for_split_delivery(vehicle, city_demand):
    isTruck = vehicle.get("type") == "truck" or vehicle.get("type") == "emergency_truck"
    roadBlocked = city_demand.get("road_status") == "Blocked"
    
    if isTruck and roadBlocked:
        return False
    return True

def get_prioritized_fleet(fleet, city_demand):
    needed_weight = city_demand["needed_weight"]
    road_status = city_demand["road_status"]
    HEAVY_LOAD = 50
    available_vehicles = [v for v in fleet if v["available"]]

    def sort_key(vehicle):
        v_type = vehicle["type"]
        # PRIORITY 1: Blocked Roads -> Drone/Heli
        if road_status == "Blocked":
            return 1 if v_type == "drone" else 2 if v_type == "heli" else 999
        # PRIORITY 2: Heavy Load -> Truck
        if needed_weight > HEAVY_LOAD:
            return 1 if v_type == "truck" else 2 if v_type == "emergency_truck" else 3
        # PRIORITY 3: Light Load -> Drone
        return 1 if v_type == "drone" else 2

    return sorted(available_vehicles, key=sort_key)

def create_emergency_vehicle(idx, is_air_support=False):
    if is_air_support:
        return {"id": f"AirLift-{idx}", "type": "heli", "capacity": 50000, "speed": "fast", "available": True}
    else:
        return {"id": f"Rental-Truck-{idx}", "type": "emergency_truck", "capacity": 5000, "speed": "slow", "available": True}

def assign_resources(flooded_cities_list):
    """
    Calculates assignments SILENTLY. 
    Returns a dictionary of detailed logs to be printed by main.py later.
    """
    fleet = initializeFleet()
    mission_logs = {}  # THIS IS THE CRITICAL DICTIONARY
    emergency_counter = 1

    priority_queue = sorted(
        [calculateDemand(c) for c in flooded_cities_list],
        key=lambda x: x['injured_count'], 
        reverse=True
    )

    for city in priority_queue:
        city_name = city["city_name"]
        needed_weight = city["needed_weight"]
        
        # --- FIX: INITIALIZE THE DICTIONARY ENTRY FIRST ---
        mission_logs[city_name] = {
            "total_demand": needed_weight,
            "status": "Pending",
            "vehicles": []
        }

        # 1. Try Normal Fleet
        candidate_vehicles = get_prioritized_fleet(fleet, city)

        for vehicle in candidate_vehicles:
            if needed_weight <= 0: break

            if check_valid_for_split_delivery(vehicle, city):
                vehicle["available"] = False
                
                delivered = min(needed_weight, vehicle["capacity"])
                needed_weight -= delivered

                mission_logs[city_name]["vehicles"].append({
                    "id": vehicle["id"],
                    "cargo": delivered
                })

        # 2. Emergency Fleet (If still needed)
        while needed_weight > 0:
            road_blocked = city["road_status"] == "Blocked"
            emergency_vehicle = create_emergency_vehicle(emergency_counter, is_air_support=road_blocked)
            emergency_counter += 1
            
            delivered = min(needed_weight, emergency_vehicle["capacity"])
            needed_weight -= delivered
            
            mission_logs[city_name]["vehicles"].append({
                "id": emergency_vehicle["id"],
                "cargo": delivered,
                "is_emergency": True
            })

        # 3. Final Status Update
        mission_logs[city_name]["remaining_demand"] = needed_weight # This line caused your crash before because the dict wasn't initialized!
        
        if needed_weight <= 0:
            mission_logs[city_name]["status"] = "Fulfilled"
        else:
            mission_logs[city_name]["status"] = "Partial/Failed"

    return mission_logs