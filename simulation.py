import copy
import random


# ==========================================================
# 1. DATA INITIALIZATION FUNCTION
# ==========================================================

def initialize_simulation_data(punjab_cities):
    # CREATE DEEP COPY TO PROTECT ORIGINAL DATASET
    sim_data = copy.deepcopy(punjab_cities)

    for city_name, data in sim_data.items():
        # INITIALIZE DYNAMIC SIMULATION FIELDS
        data["injured_count"] = 0
        data["road_status"] = "Open"
        data["priority_score"] = 0.0
        data["flood_status"] = False
        data["severity"] = 0.0

    return sim_data


# ==========================================================
# 2. PRIORITY AND IMPACT CALCULATION LOGIC
# ==========================================================

def update_priority_score(city_data):
    # FORMULA PRIORITY = INJURIES * 10 + SEVERITY * 500
    injuries = city_data["injured_count"]
    severity = city_data["severity"]

    score = (injuries * 10) + (severity * 500)
    city_data["priority_score"] = round(score, 2)


def process_flood_impact(city_name, new_severity, cities_data):
    # GET CITY DATA OBJECT
    city = cities_data[city_name]
    current_severity = city.get('severity', 0.0)

    # ONLY UPDATE IF NEW WAVE IS STRONGER THAN EXISTING RECORD
    if new_severity > current_severity:
        # UPDATE SEVERITY AND STATUS
        city['severity'] = round(new_severity, 2)
        city['flood_status'] = True

        # ROLL FOR ROAD BLOCKAGE BASED ON NEW SEVERITY
        if random.random() < new_severity:
            city['road_status'] = "Blocked"

        # CALCULATE INJURIES BASED ON POPULATION AND RISK FACTOR
        population = city.get('population', 10000)
        risk_factor = random.uniform(0.005, 0.02)
        new_injuries = int(population * new_severity * risk_factor)

        # UPDATE INJURIES USING MAX TO PREVENT REDUCTION
        city['injured_count'] = max(city['injured_count'], new_injuries)

        # RECALCULATE PRIORITY SCORE
        update_priority_score(city)

        # RETURN TRUE TO INDICATE AN UPDATE OCCURRED
        return True

    # RETURN FALSE IF NO UPDATE WAS NEEDED
    return False


# ==========================================================
# 3. FLOOD SPREAD SIMULATION ENGINE
# ==========================================================

def run_flood_simulation(start_city, cities_data, max_cities_limit=25):
    # VALIDATE START CITY EXISTS
    if start_city not in cities_data:
        print(f"Error: {start_city} not found in dataset.")
        return

    print(f"SIMULATION STARTED: Flood Surge at {start_city}...")

    # QUEUE STORES TUPLES OF CITY NAME AND SEVERITY
    queue = [(start_city, 1.0)]

    # TRACK BEST SEVERITY TO ALLOW REVISITING WITH STRONGER FLOODS
    best_severity_map = {start_city: 1.0}

    # COUNTER FOR UNIQUE CITIES FLOODED
    cities_flooded_count = 0

    while queue:
        # CHECK LIMIT ONLY IF QUEUE EMPTY TO ALLOW UPDATES TO FINISH
        if cities_flooded_count >= max_cities_limit and not queue:
            print("LIMIT REACHED STOPPING SIMULATION")
            break

        # GET NEXT CITY FROM QUEUE
        current_city_name, current_severity = queue.pop(0)

        # PHYSICS THRESHOLD STOP IF WATER ENERGY TOO LOW
        if current_severity < 0.15:
            continue

        # PROCESS IMPACT AND CHECK IF UPDATE HAPPENED
        was_updated = process_flood_impact(current_city_name, current_severity, cities_data)

        # ------------------------------------------------------
        # SPREAD TO NEIGHBORS
        # ------------------------------------------------------
        curr_elev = cities_data[current_city_name]['elevation']
        neighbors = cities_data[current_city_name]['neighbors']

        for neighbor_name in neighbors:
            # SKIP IF NEIGHBOR DOES NOT EXIST IN DATASET
            if neighbor_name not in cities_data:
                continue

            neigh_elev = cities_data[neighbor_name]['elevation']

            # DETERMINE FLOW PROBABILITY BASED ON ELEVATION
            flow_prob = 1.0 if neigh_elev < curr_elev else 0.3

            if random.random() < flow_prob:
                # APPLY DECAY FACTOR OF 0.9
                new_severity = current_severity * 0.9

                # CHECK IF THIS PATH IS STRONGER THAN PREVIOUS BEST
                previous_best = best_severity_map.get(neighbor_name, -1.0)

                if new_severity > previous_best:
                    # UPDATE BEST SEVERITY RECORD
                    best_severity_map[neighbor_name] = new_severity

                    # ADD TO QUEUE FOR PROCESSING
                    queue.append((neighbor_name, new_severity))

                    # INCREMENT COUNTER ONLY FOR NEWLY DISCOVERED CITIES
                    if previous_best == -1.0:
                        cities_flooded_count += 1

    print(f"SIMULATION COMPLETE Total Affected Cities {cities_flooded_count}")

    # Convert the map of flooded cities to a clean list of names
    flooded_cities_list = list(best_severity_map.keys())
    
    # Return this list so your code can use it
    return flooded_cities_list