import math
import random

# Logistics Hubs
HUBS = ["Lahore", "Rawalpindi"]

def calculate_haversine_distance(city_a_name, city_b_name, cities_data):
    """
    Calculates the Great Circle distance (in Kilometers) between two cities
    using the Haversine formula.
    """
    # 1. Validation
    if city_a_name not in cities_data or city_b_name not in cities_data:
        print("Error: Cities not found")
        return float('inf')

    # 2. Extract Coordinates
    lat1, lon1 = cities_data[city_a_name]['coords']
    lat2, lon2 = cities_data[city_b_name]['coords']

    # 3. Convert Decimal Degrees to Radians (Required for trig functions)
    phi1, phi2 = math.radians(lat1), math.radians(lat2)
    dphi = math.radians(lat2 - lat1)
    dlambda = math.radians(lon2 - lon1)

    # 4. Haversine Formula
    # R is Earth's radius (mean radius = 6,371km)
    R = 6371.0 
    
    a = (math.sin(dphi / 2) ** 2) + \
        (math.cos(phi1) * math.cos(phi2) * math.sin(dlambda / 2) ** 2)
    
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    
    distance_km = R * c
    
    return round(distance_km, 2)


def select_best_hub(target_city, cities_data):
    """
    Decides whether to dispatch from Lahore or Islamabad.
    """
    best_hub = None
    shortest_dist = float('inf')
    
    print(f"LOGISTICS: Calculating optimal hub for target: {target_city}...")
    
    for hub in HUBS:
        dist = calculate_haversine_distance(hub, target_city, cities_data)
        print(f" - Distance from {hub}: {dist:.4f} units")
        
        if dist < shortest_dist:
            shortest_dist = dist
            best_hub = hub
            
    print(f" -> SELECTED HUB: {best_hub}")
    print(f" -> Dispatching supplies from: {best_hub}")
    return best_hub


def get_random_valid_path(start_node, target_node, graph_data, max_attempts=100):
    """
    Tries to find ONE random path from start to target.
    Returns the path (list of strings) or None if it fails.
    """
    for _ in range(max_attempts):
        # 1. Start a new journey
        path = [start_node]
        current_node = start_node
        visited = {start_node}
        
        # 2. Walk until we reach target or get stuck
        while current_node != target_node:
            neighbors = list(graph_data[current_node]['neighbors'].keys())
            
            # Filter neighbors: Only move to ones we haven't visited yet
            valid_moves = [n for n in neighbors if n not in visited]
            
            if not valid_moves:
                # Dead end! Break inner loop to restart this attempt
                break
            
            # 3. Pick a random next step
            next_move = random.choice(valid_moves)
            
            # 4. Move there
            path.append(next_move)
            visited.add(next_move)
            current_node = next_move
            
            # Success check
            if current_node == target_node:
                return path
                
    return None # Failed to find a path after many tries


def create_initial_population(start_node, target_node, graph_data, pop_size=20):
    """
    Generates a list of random valid paths.
    """
    population = []
    attempts = 0
    
    print(f"[GA] Searching for {pop_size} unique paths from {start_node} to {target_node}...")
    
    while len(population) < pop_size:
        # Try to generate a path
        path = get_random_valid_path(start_node, target_node, graph_data)
        
        if path:
            # OPTIONAL: Avoid exact duplicates in the population
            if path not in population:
                population.append(path)
        
        # Safety break to prevent infinite loops if paths are impossible
        attempts += 1
        if attempts > pop_size * 10:
            print(f"Warning: Only found {len(population)} paths (Graph might be disconnected or too small).")
            break
            
    return population


def calculate_fitness(path, graph_data):
    """
    Scores a path. 
    High Score = Low Distance AND Low Flood Risk.
    """
    total_distance = 0
    total_risk = 0
    
    # Loop through the path to calculate costs
    for i in range(len(path) - 1):
        current_city = path[i]
        next_city = path[i+1]
        
        # 1. GET REAL DISTANCE from your dataset
        # accessing graph_data['Ahmadpur Sial']['neighbors']['Shorkot'] -> 35
        try:
            segment_dist = graph_data[current_city]['neighbors'][next_city]
        except KeyError:
            # If data is missing (broken path), penalize heavily
            return 0 
            
        total_distance += segment_dist
        
        # 2. GET FLOOD RISK from the simulation status
        # We check the node we are entering (next_city)
        node_data = graph_data[next_city]
        
        # Immediate Fail: Road Blocked
        if node_data.get('road_status') == "Blocked":
            return 0.1 # Almost zero fitness
            
        # Accumulate Severity (e.g., 0.0 to 1.0)
        # We multiply by 100 to make it weigh heavily against distance
        total_risk += (node_data.get('severity', 0) * 100)

    # 3. FINAL FORMULA
    # We want to MINIMIZE (Distance + Risk). 
    # Since GA maximizes Fitness, we divide 1 by the cost.
    total_cost = total_distance + total_risk
    
    if total_cost == 0: return 9999 # Perfect path (unlikely)
    
    return 10000 / total_cost


def mutate_path(path, target_node, graph_data, mutation_rate=0.3):
    """
    Tries to alter a path to find a new route.
    Logic: Keep the start of the path, cut the tail, and generate a new random tail.
    """
    # 1. Roll the dice (Mutation Rate)
    if random.random() > mutation_rate:
        return path # No mutation happens
        
    # Safety: Cannot mutate a path that is too short (e.g., [Start, End])
    if len(path) < 3:
        return path
        
    # 2. Pick a "Break Point" (excluding Start and Target)
    # We pick an index between 1 and length-2
    cut_index = random.randint(1, len(path) - 2)
    break_point_city = path[cut_index]
    
    # 3. Keep the "Head" (Start -> Break Point)
    new_path_head = path[:cut_index+1]
    
    # 4. Try to "Regrow" the Tail (Break Point -> Target)
    # We use our existing random walker helper
    new_tail = get_random_valid_path(break_point_city, target_node, graph_data)
    
    if new_tail:
        # Success! Splice them together.
        # Note: new_tail includes the break_point_city at index 0, so we slice it off to avoid duplicate
        return new_path_head + new_tail[1:]
        
    # If regrowth failed (dead end), return original path
    return path