import streamlit as st
import os
from PIL import Image
from datetime import datetime
import folium
from streamlit_folium import st_folium
import sqlite3

# Directory to save images
image_dir = "images"

# Create the directory if it doesn't exist
if not os.path.exists(image_dir):
    os.makedirs(image_dir)

# Connect to SQLite database
conn = sqlite3.connect('complaints.db')
c = conn.cursor()

# Check if the table already exists
c.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='complaints'")
table_exists = c.fetchone()

# Create table if it doesn't exist
if not table_exists:
    c.execute('''CREATE TABLE complaints
                 (id INTEGER PRIMARY KEY, Complaint_Number TEXT, name TEXT, latitude REAL, longitude REAL, description TEXT, Address TEXT, Phone_Number TEXT, image_path TEXT, timestamp TEXT)''')
    conn.commit()

# Streamlit title
st.title("Geotagged Garbage Complaint Dashboard")

# Complaint Form
st.header("Submit a Complaint")
name = st.text_input("Your Name")

# Add a map for selecting the location
st.header("Select Location")
Note = st.text("Please DOUBLE CLICK on marker after selecting the location")

# Initial map setup
initial_coords = [30.3165, 78.0322]
m = folium.Map(location=initial_coords, zoom_start=13)

# Add a draggable marker to the map
marker = folium.Marker(
    location=initial_coords,
    draggable=True
)
marker.add_to(m)

# Display the map and capture selected coordinates
map_data = st_folium(m, width=700, height=500)

# Check if a location is selected by moving the marker
selected_coords = None
if map_data and "last_object_clicked" in map_data and map_data["last_object_clicked"]:
    selected_coords = map_data["last_object_clicked"]

description = st.text_area("Description")
Address = st.text_area("Address(Landmark)")
image_file = st.file_uploader("Upload an image", type=["jpg", "jpeg", "png"])
phone_number = st.text_input("Phone Number")

if st.button("Submit"):
    if not name or not description or not image_file or not selected_coords:
        st.error("Please fill all the fields, upload an image, and select a location on the map.")
    elif not phone_number.isdigit() or len(phone_number) != 10:
        st.error("Please enter a valid 10-digit phone number.")
    else:
        lat = selected_coords["lat"]
        lng = selected_coords["lng"]

        # Generate a unique complaint number
        complaint_number = datetime.now().strftime("%Y%m%d%H%M%S")

        # Save the image with a unique name
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
        image_path = os.path.join(image_dir, f"{timestamp}_{image_file.name}")
        with open(image_path, "wb") as f:
            f.write(image_file.getbuffer())

        # Insert complaint into the database
        c.execute("INSERT INTO complaints (Complaint_Number, name, latitude, longitude, description, Address, Phone_Number, image_path, timestamp) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)",
                  (complaint_number, name, lat, lng, description, Address, phone_number, image_path, timestamp))
        conn.commit()

        st.success("Complaint submitted successfully!")
        st.info(f"Image saved at: {image_path}")
        st.info(f"Selected Location: Latitude {lat}, Longitude {lng}")

# Display Complaints
st.header("Complaints")
c.execute("SELECT Complaint_Number, name, latitude, longitude, description, Address, Phone_Number, image_path, timestamp FROM complaints")
rows = c.fetchall()

for row in rows:
    st.subheader(f"Complaint Number {row[0]}  at {row[5]}, Latitude {row[2]}, Longitude {row[3]} on {row[8]}")
    st.image(row[7], caption=f"Location: Latitude {row[2]}, Longitude {row[3]}", use_column_width=True)

# Close the database connection
conn.close()
