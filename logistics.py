

#helper function to calculate cargo weight based purely on injured count.
def calculateDemand(city):
    
    injured_count = city.get("injured_count", 0)

    #for each person 5kg of supplies is needed (assumption)
    SUPPLY_PER_PERSON = 5

    needed_weight = injured_count * SUPPLY_PER_PERSON

    return {
        "city_name": city["name"],
        "injured_count": injured_count,   # PRIORITY SCORE
        "needed_weight": needed_weight,   # CONSTRAINT CHECKING
        "road_status": city["road_status"],
        "location": city["coords"]
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
    
    # 15 truck
    for i in range (1, 11):
        fleet.append({
            "id": f"Drone-{i}",
            "type": "drone",
            "capacity": 50,  # kg
            "speed": "fast",
            "available": True
        })
    
    # 2 heli
    for i in range (1, 11):
        fleet.append({
            "id": f"Helicopter-{i}",
            "type": "drone",
            "capacity": 20000,  # kg
            "speed": "fast",
            "available": True
        })

    return fleet



