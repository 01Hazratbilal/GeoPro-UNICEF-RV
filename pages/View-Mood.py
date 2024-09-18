# view.py

import streamlit as st
import folium
from streamlit_folium import st_folium
from folium.plugins import Draw, Fullscreen
import json
import os
from streamlit_extras.switch_page_button import switch_page

st.set_page_config(layout="wide")

# Hide the Sidebar
st.markdown("""
            <style>
            [data-testid="stSidebar"] {
                display: none
            }

            [data-testid="collapsedControl"] {
                display: none
            }
            </style>
            """, unsafe_allow_html=True)


# Load configuration data
@st.cache_data
def load_config():
    with open('config.json', 'r') as f:
        return json.load(f)

config = load_config()
ICON_URLS = config["ICON_URLS"]

def ensure_files_exist():
    for filename in ['shapes.json', 'markers.json']:
        if not os.path.exists(filename):
            with open(filename, 'w') as f:
                json.dump({"type": "FeatureCollection", "features": []} if filename == 'shapes.json' else [], f)

@st.cache_resource
def load_data(filename):
    ensure_files_exist()
    with open(filename, 'r') as f:
        return json.load(f)

def save_data(data, filename):
    with open(filename, 'w') as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

# Ensure required files exist
ensure_files_exist()

# Load previously saved markers and shapes
markers = load_data('markers.json')
shapes = load_data('shapes.json')

map_center = [30.391638, 68.434838]  # Coordinates for Loralai, Balochistan, Pakistan
zoom_start = 12

map_object = folium.Map(
    location=map_center,
    zoom_start=zoom_start,
    tiles=None
)

folium.TileLayer(
    tiles='https://mt1.google.com/vt/lyrs=y&x={x}&y={y}&z={z}',
    attr='Google Satellite',
    name='Google Satellite'
).add_to(map_object)

# Add Fullscreen plugin to map_object with position set to 'topright'
Fullscreen(position='topright').add_to(map_object)

# Add fullscreen button to the map
Fullscreen(position='topright').add_to(map_object)

c1, c2, c3 = st.columns([0.2, 1, 0.2])
with c2:
    # Horizontal Navbar for filtering
    with st.container():
        filter_options = ['Polygon', 'LineString'] + list(ICON_URLS.keys())
        selected_options = st.multiselect("", filter_options, default=filter_options)

# Function to add a custom marker
def add_custom_marker(map_object, lat, lon, icon_url, icon_name, popup_text):
    icon = folium.CustomIcon(icon_url, icon_size=(30, 30)) if icon_url else None
    place_name = get_place_name(lat, lon)
    full_popup_text = f"<b>{icon_name}</b><br>{popup_text}<br>{place_name}<br>Cordinates: {lat}, {lon}"
    popup = folium.Popup(folium.IFrame(full_popup_text, width=200, height=150))
    folium.Marker(location=[lat, lon], popup=popup, icon=icon).add_to(map_object)

def get_place_name(lat, lon):
    # Replace with actual geocoding implementation if needed
    return "Location"

# Filter markers and shapes
def should_display_marker(marker):
    return marker["icon_name"] in selected_options

def should_display_shape(shape):
    shape_type = shape['geometry']['type']
    return shape_type in selected_options

# Adding markers
for marker in markers:
    if should_display_marker(marker):
        add_custom_marker(
            map_object,
            marker["lat"],
            marker["lon"],
            marker["icon_url"],
            marker["icon_name"],
            marker["popup_text"]
        )

def count_markers_in_Jam(Ploygon_coords, markers):
    from shapely.geometry import Jam, Point

    Jam = Jam(Jam_coords)
    icon_counts = {icon: 0 for icon in ICON_URLS.keys()}
    location_details = []

    for marker in markers:
        point = Point(marker["lon"], marker["lat"])
        if Jam.contains(point):
            if marker["icon_name"] == "Location":
                location_details.append(marker["popup_text"])
            else:
                icon_counts[marker["icon_name"]] += 1

    # Create a dictionary for non-zero icon counts
    icon_counts = {icon: count for icon, count in icon_counts.items() if count > 0}

    return icon_counts, location_details

# Adding shapes
for shape in shapes['features']:
    if should_display_shape(shape):
        shape_color = shape['properties'].get('color', '#FF0000')
        geometry = shape['geometry']

        if geometry['type'] == 'Jam':
            Jam_coords = geometry['coordinates'][0]
            icon_counts, location_details = count_markers_in_Jam(Jam_coords, markers)

            # Construct the popup text
            popup_text = ""
            if location_details:
                popup_text += "<br>Location Details:<br>" + "<br>".join(location_details)
            if icon_counts:
                for icon, count in icon_counts.items():
                    popup_text += f"<br>{icon}: {count}"

            folium.GeoJson(
                shape,
                style_function=lambda feature: {'color': shape_color, 'weight': 2, 'fillOpacity': 0.05, 'opacity': 0.3},
                popup=folium.Popup(folium.IFrame(popup_text, width=200, height=150)) if popup_text else None
            ).add_to(map_object)
        elif geometry['type'] == 'LineString':
            popup_text = shape.get('properties', {}).get('description', '')
            folium.GeoJson(
                shape,
                style_function=lambda feature: {'color': '#0000FF'},  # Ensure polyline color is always blue
                popup=folium.Popup(folium.IFrame(popup_text, width=200, height=100)) if popup_text else None
            ).add_to(map_object)

# Render map
map_data = st_folium(map_object, width=1260, height=600)



col1, col2, col3 = st.columns([2.3, 1, 2])

with col2:
    if st.button("Back"):
        switch_page('Main-Page')
