

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


# Constrains CSP
def check_vehicle_assignment(vehicle, city_demand):

    """
    Validates if a specific vehicle can handle a specific city's request.
    Returns: True (Valid) or False (Invalid)
    """

    # contraint 1
    # if vehicle capacity >= cargo weight
    vehicle_capacity = vehicle.get("capacity", 0) 
    required_weight = city_demand.get("needed_weight", 0)

    if vehicle_capacity < required_weight:
        return False
    
    # constriant 2
    # if road is blocked and vehicle is truck
    isTruck = vehicle.get("type")
    roadBlocked = city_demand.get("road_status")
    
    if isTruck and roadBlocked:
        return False
    
    # if both constraints satisty
    return True


    





