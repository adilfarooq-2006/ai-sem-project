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
    
    # Weight Thresholds
    HEAVY_LOAD_TRUCK = 50
    HEAVY_LOAD_AIR = 500  # New threshold for switching from Drone to Heli
    
    available_vehicles = [v for v in fleet if v["available"]]

    def sort_key(vehicle):
        v_type = vehicle["type"]
        
        # PRIORITY 1: Blocked Roads -> Air Support
        if road_status == "Blocked":
            # Logic Update: If load is heavy (>500kg), prioritize Heli over Drone
            if needed_weight > HEAVY_LOAD_AIR:
                return 1 if v_type == "heli" else 2 if v_type == "drone" else 999
            else:
                # Light load: Drones are cheaper/faster to deploy
                return 1 if v_type == "drone" else 2 if v_type == "heli" else 999
                
        # PRIORITY 2: Open Roads + Heavy Load -> Truck
        if needed_weight > HEAVY_LOAD_TRUCK:
            return 1 if v_type == "truck" else 2 if v_type == "emergency_truck" else 3
            
        # PRIORITY 3: Open Roads + Light Load -> Drone (or whatever acts as courier)
        return 1 if v_type == "drone" else 2

    return sorted(available_vehicles, key=sort_key)

    return sorted(available_vehicles, key=sort_key)

def create_emergency_vehicle(idx, is_air_support=False):
    if is_air_support:
        return {"id": f"AirLift-{idx}", "type": "heli", "capacity": 50000, "speed": "fast", "available": True}
    else:
        return {"id": f"Rental-Truck-{idx}", "type": "emergency_truck", "capacity": 5000, "speed": "slow", "available": True}
    

def assign_resources(flooded_cities_list):
    """
    Calculates assignments and PRINTS logs immediately.
    No return value.
    """
    # Assuming initializeFleet() and calculateDemand() are defined elsewhere in your code
    fleet = initializeFleet() 
    emergency_counter = 1

    print("\n" + "="*50)
    print("[LOGISTICS] Assigning Resources...")
    print("="*50 + "\n")

    priority_queue = sorted(
        [calculateDemand(c) for c in flooded_cities_list],
        key=lambda x: x['injured_count'], 
        reverse=True
    )

    for city in priority_queue:
        city_name = city["city_name"]
        needed_weight = city["needed_weight"]
        original_demand = needed_weight # Keep track for logging
        assigned_vehicles_log = []

        # Try Normal Fleet
        candidate_vehicles = get_prioritized_fleet(fleet, city)

        for vehicle in candidate_vehicles:
            if needed_weight <= 0: 
                print(f"\n[LOGISTICS] Demand of {city_name} is fullfilled")
                break

            if check_valid_for_split_delivery(vehicle, city):
                
                vehicle["available"] = False
                
                delivered = min(needed_weight, vehicle["capacity"])
                needed_weight -= delivered

                assigned_vehicles_log.append(f"{vehicle['id']} ({delivered}kg)")

        # 2. Emergency Fleet (If still needed)
        while needed_weight > 0:
            road_blocked = city["road_status"] == "Blocked"
            
            # Logic: If blocked, create Heli. If open, create Truck.
            emergency_vehicle = create_emergency_vehicle(emergency_counter, is_air_support=road_blocked)
            emergency_counter += 1
            
            delivered = min(needed_weight, emergency_vehicle["capacity"])
            needed_weight -= delivered
            
            assigned_vehicles_log.append(f"EMERGENCY: {emergency_vehicle['id']} ({delivered}kg)") 

        # 3. Print Logs Immediately
        status = "Fulfilled" if needed_weight <= 0 else "Partial/Failed"
        
        print(f"CITY: {city_name.upper()}")
        print(f"  - Road Status: {city['road_status']}")
        print(f"  - Total Demand: {original_demand} kg")
        print(f"  - Status: {status}")
        print(f"  - Assigned Fleet:")
        if assigned_vehicles_log:
            for log in assigned_vehicles_log:
                print(f"   -> {log}")
        else:
            print(f"-> No vehicles assigned.")
        
        print("-" * 30) # Separator for next city