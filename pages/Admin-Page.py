import streamlit as st
import folium
from streamlit_folium import st_folium
from folium.plugins import Draw
from geopy.geocoders import Nominatim
import json
import os
import uuid
from shapely.geometry import Polygon, Point
from streamlit_extras.switch_page_button import switch_page

st.set_page_config(layout="wide")

# Hide the Sidebar
st.markdown(
    """
<style>
    [data-testid="collapsedControl"] {
        display: none
    }
</style>
""",
    unsafe_allow_html=True,
)

# Initialize geocoder
geolocator = Nominatim(user_agent="geoapiExercises")

# Load configuration data
@st.cache_data
def load_config():
    with open('config.json', 'r') as f:
        return json.load(f)

config = load_config()
ICON_URLS = config["ICON_URLS"]

@st.cache_data
def get_place_name(lat, lon):
    try:
        location = geolocator.reverse((lat, lon), exactly_one=True)
        return location.address if location else "Unknown place"
    except:
        return "Unknown place"

def add_custom_marker(map_object, lat, lon, icon_url, icon_name, popup_text):
    icon = folium.CustomIcon(icon_url, icon_size=(30, 30)) if icon_url else None
    place_name = get_place_name(lat, lon)
    full_popup_text = f"<b>{icon_name}</b><br>{popup_text}<br>{place_name}<br>Cordinates: {lat}, {lon}"
    popup = folium.Popup(folium.IFrame(full_popup_text, width=200, height=150))
    folium.Marker(location=[lat, lon], popup=popup, icon=icon).add_to(map_object)

@st.cache_resource
def load_data(filename, default=None):
    if os.path.exists(filename):
        with open(filename, 'r') as f:
            return json.load(f)
    return default or {"type": "FeatureCollection", "features": []}

def save_data(data, filename):
    with open(filename, 'w') as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

# Load previously saved markers and shapes
markers = load_data('markers.json', [])
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

# Sidebar sections
with st.sidebar.expander("Customize Drawing", expanded=False):
    # Color picker for polygons
    polygon_color = st.color_picker("Select Jam color", "#FF0000")

draw = Draw(
    draw_options={
        'polyline': {'shapeOptions': {'color': '#0000FF', 'weight': 3, 'fillOpacity': 0.5}},  # Set polyline color to blue
        'polygon': {'shapeOptions': {'color': polygon_color, 'weight': 1, 'fillOpacity': 0.05}},  # Use selected polygon color
        'circle': False,
        'rectangle': False,
        'circlemarker': False,
        'marker': False
    },
    edit_options={
        'edit': False,  # Disable editing
        'remove': False  # Disable removal
    }
)
draw.add_to(map_object)

# Horizontal Navbar for filtering
with st.container():
    filter_options = ['Jam', 'Pipe Line'] + list(ICON_URLS.keys())
    selected_options = st.multiselect("", filter_options, default=filter_options)

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

def count_markers_in_polygon(polygon_coords, markers):
    polygon = Polygon(polygon_coords)
    icon_counts = {icon: 0 for icon in ICON_URLS.keys()}
    location_details = []

    for marker in markers:
        point = Point(marker["lon"], marker["lat"])
        if polygon.contains(point):
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
            polygon_coords = geometry['coordinates'][0]
            icon_counts, location_details = count_markers_in_polygon(polygon_coords, markers)

            # Construct the popup text
            popup_text = ""
            if icon_counts:
                for icon, count in icon_counts.items():
                    popup_text += f"{icon}: {count}<br>"

            if location_details:
                popup_text += "<br>Location Details:<br>" + "<br>".join(location_details)

            folium.GeoJson(
                shape,
                style_function=lambda feature: {'color': shape_color, 'weight': 2, 'fillOpacity': 0.05, 'opacity': 0.3},
                popup=folium.Popup(folium.IFrame(popup_text, width=200, height=150)) if popup_text else None
            ).add_to(map_object)
        elif geometry['type'] == 'Pipe Line':
            popup_text = shape.get('properties', {}).get('description', '')
            folium.GeoJson(
                shape,
                style_function=lambda feature: {'color': '#0000FF'},  # Ensure polyline color is always blue
                popup=folium.Popup(folium.IFrame(popup_text, width=200, height=100)) if popup_text else None
            ).add_to(map_object)

# Render map
map_data = st_folium(map_object, width=910, height=500)

if map_data and 'last_clicked' in map_data and map_data['last_clicked']:
    st.session_state.latitude = map_data['last_clicked']['lat']
    st.session_state.longitude = map_data['last_clicked']['lng']

if map_data and 'all_drawings' in map_data:
    new_shapes = map_data['all_drawings']
    if new_shapes:
        for shape in new_shapes:
            shape['id'] = str(uuid.uuid4())
            shape['properties'] = shape.get('properties', {})
            shape_color = shape.get('properties', {}).get('color', polygon_color)
            shape['properties']['color'] = shape_color
        shapes['features'].extend(new_shapes)
        save_data(shapes, 'shapes.json')

# Sidebar sections
with st.sidebar.expander("Add a Marker", expanded=False):
    latitude = st.number_input("Latitude", value=st.session_state.get('latitude', map_center[0]), format="%.14f")
    longitude = st.number_input("Longitude", value=st.session_state.get('longitude', map_center[1]), format="%.14f")
    icon_name = st.selectbox("Select Icon Type", list(ICON_URLS.keys()))
    icon_url = ICON_URLS[icon_name]

    if icon_name == "Location":
        representative = st.text_input("Representative", placeholder="Representative name")
        description = st.text_area("Description", placeholder="Write something here...")
        popup_text = f"Representative: {representative}<br> {description}"
    else:
        popup_text = st.text_area("Popup Text", placeholder="Your info here...")

    add_marker_button = st.button("Add Marker")

    if add_marker_button:
        add_custom_marker(map_object, latitude, longitude, icon_url, icon_name, popup_text)
        new_marker = {"lat": latitude, "lon": longitude, "icon_url": icon_url, "icon_name": icon_name, "popup_text": popup_text}
        markers.append(new_marker)
        save_data(markers, 'markers.json')
        st.experimental_rerun()

with st.sidebar.expander("Delete a Marker", expanded=False):
    if markers:
        marker_names = [f"{m['icon_name']} at ({m['lat']:.5f}, {m['lon']:.5f})" for m in markers]
        selected_marker = st.selectbox("Select Marker to Delete", marker_names)
        if st.button("Delete Selected Marker"):
            marker_index = marker_names.index(selected_marker)
            markers.pop(marker_index)
            save_data(markers, 'markers.json')
            st.success("Marker deleted successfully.")
            st.experimental_rerun()
    else:
        st.write("No markers available to delete.")

with st.sidebar.expander("Delete a Shape", expanded=False):
    if shapes['features']:
        shape_ids = [shape.get('id', str(index)) for index, shape in enumerate(shapes['features'])]
        selected_shape_id = st.selectbox("Select Shape to Delete", shape_ids)
        if st.button("Delete Selected Shape"):
            shapes['features'] = [shape for shape in shapes['features'] if shape.get('id') != selected_shape_id]
            save_data(shapes, 'shapes.json')
            st.success("Shape deleted successfully.")
            st.experimental_rerun()
    else:
        st.write("No shapes available to delete.")




col1, col2, col3 = st.columns([2.3, 1, 2])

with col2:
    if st.button("Back"):
        switch_page('Main-Page')