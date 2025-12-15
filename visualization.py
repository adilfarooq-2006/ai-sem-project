import folium
import folium.plugins # Helper for AntPath
import os

def generate_mission_map(active_data, path=None, filename="mission_map.html", output_folder="maps"):
    """
    Generates an interactive HTML map.
    - Red Markers: Flooded Cities (with stats)
    - Green Markers: Safe Cities / Hubs
    - Blue Line: The Rescue Route
    """

    if not os.path.exists(output_folder):
        os.makedirs(output_folder)
        print(f"[SYSTEM] Created new folder: '{output_folder}'")
    
    # 1. Create Base Map (Centered on Punjab)
    # Coordinates for roughly the center of Punjab
    m = folium.Map(location=[31.1704, 72.7097], zoom_start=7)

    # 2. Add City Markers
    for city_name, data in active_data.items():
        coords = data.get('coords')
        
        # Determine Color & Icon
        if data.get('flood_status', False):
            color = 'red'
            icon = 'exclamation-triangle'
            status_text = f"FLOODED (Severity: {data.get('severity', 0):.2f})"
        else:
            color = 'green'
            icon = 'home'
            status_text = "Safe"
            
        # Add Hub Marker Special Color (Optional)
        if city_name in ["Lahore", "Rawalpindi"]:
            color = 'blue' if not data.get('flood_status') else 'red'
            icon = 'plane'

        # Popup Info
        popup_content = f"""
        <b>{city_name}</b><br>
        Status: {status_text}<br>
        Injured: {data.get('injured_count', 0)}<br>
        Roads: {data.get('road_status', 'Open')}
        """

        folium.Marker(
            location=coords,
            popup=popup_content,
            tooltip=city_name,
            icon=folium.Icon(color=color, icon=icon, prefix='fa')
        ).add_to(m)

    # 3. Draw the Route (Polyline)
    if path:
        route_coords = []
        for city in path:
            if city in active_data:
                route_coords.append(active_data[city]['coords'])
        
        # Add the line
        folium.PolyLine(
            route_coords,
            color="blue",
            weight=4,
            opacity=0.7,
            tooltip="Rescue Route"
        ).add_to(m)
        
        # Add moving marker effect (Optional - purely visual)
        folium.plugins.AntPath(route_coords).add_to(m)

    # 5. Save Map to the Folder
    full_path = os.path.join(output_folder, filename)
    m.save(full_path)
    
    print(f"\n[VISUALIZATION] Map saved to: '{full_path}'")
