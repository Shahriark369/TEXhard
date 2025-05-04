import streamlit as st
from pymongo import MongoClient
from datetime import datetime
import os
from PIL import Image
import io

st.set_page_config(
    page_title="⚡TEXhard drop the question💡",
    page_icon="🧠"
)

# MongoDB Setup (replace with your URI)
MONGO_URI = os.getenv("MONGO_URI")
client = MongoClient(MONGO_URI)
db = client["notification_db"]
collection = db["uploads"]

# Ensure uploads folder exists
if not os.path.exists("uploads"):
    os.makedirs("uploads")

st.title("TEXhard তোমার সাথে হোক আমাদেরও রিভিশন")

# Input form
with st.form("upload_form"):
    name = st.text_input("Enter your name")
    uploaded_file = st.file_uploader("Upload an image", type=["jpg", "jpeg", "png"])
    submit = st.form_submit_button("Submit")

    if submit:
        if not name or not uploaded_file:
            st.error("Please enter your name and upload an image.")
        else:
            # Save image to 'uploads/' folder
            timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
            filename = f"{name}_{timestamp}.png"
            filepath = os.path.join("uploads", filename)

            image = Image.open(uploaded_file)
            image.save(filepath)

            # Insert into MongoDB
            doc = {
                "name": name,
                "filename": filename,
                "timestamp": datetime.now()
            }
            collection.insert_one(doc)

            st.success("Image uploaded successfully!")

# Display all uploaded images
st.subheader("Uploaded Images:")
docs = collection.find().sort("timestamp", -1)
for doc in docs:
    st.markdown(f"**{doc['name']}** uploaded:")
    img_path = os.path.join("uploads", doc['filename'])
    if os.path.exists(img_path):
        st.image(img_path, width=300)

import time

# Polling interval (seconds)
POLL_INTERVAL = 5  

# Initialize session state
if 'last_checked' not in st.session_state:
    st.session_state.last_checked = datetime.now()

if 'notified' not in st.session_state:
    st.session_state.notified = False

# Check if a new image was added
latest_upload = collection.find_one(sort=[("timestamp", -1)])
if latest_upload and latest_upload["timestamp"] > st.session_state.last_checked:
    if not st.session_state.notified:
        st.toast("🔔 Someone just uploaded a new image!")
        st.session_state.notified = True
        st.session_state.last_checked = latest_upload["timestamp"]
