
#helper function to calculate cargo weight based purely on injured count.
def calculateDemand(flooded_city_data):
    
    injured_count = flooded_city_data.get("injured_count", 0)

    #for each person 5kg of supplies is needed (assumption)
    SUPPLY_PER_PERSON = 5

    needed_weight = injured_count * SUPPLY_PER_PERSON

    return {
        "city_name": flooded_city_data["name"],
        "injured_count": injured_count,   # PRIORITY SCORE
        "needed_weight": needed_weight,   # CONSTRAINT CHECKING
        "road_status": flooded_city_data["road_status"],
        "location": flooded_city_data["coords"]
    }


# vehicle resourses
def initializeFleet():
    
    fleet = []

    # 10 truck
    for i in range (1, 11):
        fleet.append({
            "id": f"Truck-{i}",
            "type": "truck",
            "capacity": 2500,  # kg (Example High Cap)
            "speed": "slow",
            "available": True
        })
    
    # 15 drone
    for i in range (1, 16):
        fleet.append({
            "id": f"Drone-{i}",
            "type": "drone",
            "capacity": 50,  # kg
            "speed": "fast",
            "available": True
        })
    
    # 2 heli
    for i in range (1, 3):
        fleet.append({
            "id": f"Helicopter-{i}",
            "type": "heli",
            "capacity": 20000,  # kg
            "speed": "fast",
            "available": True
        })

    return fleet


# Constraints CSP
def check_valid_for_split_delivery(vehicle, city_demand):

    """
    Validates if a specific vehicle can handle a specific city's request.
    Returns: True (Valid) or False (Invalid)
    """
    # if road is blocked and vehicle is truck
    isTruck = vehicle.get("type")
    roadBlocked = city_demand.get("road_status")
    
    if isTruck and roadBlocked:
        return False
    
    # if both constraints satisty
    return True


def get_prioritized_fleet(fleet, city_demand):
    """
    Sorts the fleet based on the specific rules:
    1. Road Open + Heavy Load -> Truck First
    2. Road Blocked -> Drones, then Heli (Trucks invalid)
    3. Light Load -> Drones First
    4. Helicopters -> Always Last Resort
    """

    needed_weight = city_demand["needed_weight"]
    road_status = city_demand["road_status"]

    # if weight is > 50 it wont be assigned to drones
    HEAVY_LOAD = 50

    #check to get vehicles that are available
    available_vehicles = [v for v in fleet if v["available"]]
    

    def sort_key(vehicle):
        vehicle_type = vehicle["type"]
        vehicle_capacity = vehicle["capacity"]

        # constraint 1 - ROAD IS BLOCKED
        if road_status == "Blocked" and vehicle_type == "truck":
            return 999
        
        # constraint 2 : heavy load & more injured and roads OPEN
        # Preference: Truck (1) -> Drone (2) -> Heli (3)
        if needed_weight > HEAVY_LOAD and road_status == "Open":
            
            if vehicle_type == "truck":
                return 1
            if vehicle_type == "drone":
                return 2
            if vehicle_type == "heli":
                return 3
            
        # constraint heavy load & road == BLOCKED
        if needed_weight > HEAVY_LOAD and road_status == "Blocked":
            if vehicle_type == "drone":
                return 1
            if vehicle_type == "heli":
                return 2
            
        # constraint 3 - less injured people
        # Preference: Drone (1) -> Truck (2) -> Heli (3)
        if vehicle_type == "drone":
            return 1
        if vehicle_type == "truck":
            return 2
        if vehicle_type == "heli":
            return 3

        return 4 # Default fallback
    # Return the fleet sorted by these custom rules
    # Python internally does a loop like this:
    # ranks = []
    # for v in available_vehicles:
    #     r = sort_key(v)  <- PYTHON CALLS YOUR FUNCTION HERE
    #     ranks.append(r)
    return sorted(available_vehicles, key=sort_key)


def assign_resources(flooded_cities_list):
    """
    Allocates multiple vehicles to cities until demand is met.
    """
    print("[CSP MANAGER] Starting Dynamic Split Delivery...")

    fleet  = initializeFleet()
    assignments = {} #format: { "CityName": ["Truck-1", "Drone-2"] }

    #sort cities by priority
    priority_queue = sorted(
        [calculateDemand(c) for c in flooded_cities_list],
        key=lambda x: x['injured_count'], 
        reverse=True
    )

    for city in priority_queue:
        city_name = city["city_name"]
        needed_weight = city["needed_weight"]

        #intialize list for each city
        assignments[city_name] = []

        # Get prioritized fleet (Trucks -> Drones -> Helis)
        # We RE-EVALUATE this for every city to check who is still available
        candidate_vehicles = get_prioritized_fleet(fleet, city)
        
        print(f"Processing {city_name}: Needs {needed_weight}kg")

        for vehicle in candidate_vehicles:
            # Stop if we have fulfilled the demand
            if needed_weight <= 0:
                print(f"  -> {city_name} is fully supplied!")
                break

            # check HARD constraints if passed then start
            if check_valid_for_split_delivery(vehicle, city):

                # remove availibilty of vehile
                vehicle["available"] = False
                assignments[city_name].append(vehicle["id"])

                #subtarct cargp 
                delivered_amount = min(needed_weight, vehicle["capacity"])
                needed_weight -= delivered_amount

                print(f"    -> Assigned {vehicle['id']} (Delivers {delivered_amount}kg). Remaining: {needed_weight}kg")

        # if cargo is still more and available vehiocles are all routed
        if needed_weight > 0:
            print(f"  -> WARNING: {city_name} still needs {needed_weight}kg. Fleet exhausted!")
    
    return assignments