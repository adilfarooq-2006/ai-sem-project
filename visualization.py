import folium
import folium.plugins
import os


def generate_mission_map(active_data, path=None, assignments=None, filename="mission_map.html", output_folder="maps"):
    """
    Generates an interactive HTML map.
    - Blue Line (Default): Helicopter Support
    - Green Line: Ground Trucking
    - Orange Line: Drone Swarm
    """
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)

    # 1. Create Base Map
    m = folium.Map(location=[31.1704, 72.7097], zoom_start=7)

    # 2. DEFAULT COLOR LOGIC
    # We set Heli (Blue) as the default starting point
    path_color = "blue"
    vehicle_label = "Helicopter Support"

    if assignments:
        log_str = " ".join(assignments).lower()

        # If 'truck' is found, override default to Green
        if "truck" in log_str or "rental" in log_str:
            path_color = "green"
            vehicle_label = "Ground Trucking"

        # If 'drone' is found, override default to Orange
        elif "drone" in log_str:
            path_color = "orange"
            vehicle_label = "Drone Swarm"

        # Note: If 'heli' is found, it stays 'blue' (the default)

    # 3. Add City Markers
    for city_name, data in active_data.items():
        coords = data.get('coords')
        is_flooded = data.get('flood_status', False)
        m_color = 'red' if is_flooded else 'green'

        # Hubs get a special icon
        if city_name in ["Lahore", "Rawalpindi"]:
            m_color = 'cadetblue'

        folium.Marker(
            location=coords,
            tooltip=f"{city_name} ({'FLOODED' if is_flooded else 'Safe'})",
            icon=folium.Icon(color=m_color, icon='exclamation-triangle' if is_flooded else 'home', prefix='fa')
        ).add_to(m)

    # 4. Draw the Rescue Path
    if path:
        route_coords = [active_data[city]['coords'] for city in path if city in active_data]

        # Main Line
        folium.PolyLine(
            route_coords,
            color=path_color,
            weight=5,
            opacity=0.8,
            tooltip=f"Mission: {vehicle_label}"
        ).add_to(m)

        # Animated "Ant" Effect
        folium.plugins.AntPath(
            route_coords,
            color=path_color,
            pulse_color='white'
        ).add_to(m)

    # 5. Save the Map
    full_path = os.path.join(output_folder, filename)
    m.save(full_path)
    print(f"[VISUALIZATION] Map saved: '{full_path}' (Path Color: {path_color})")