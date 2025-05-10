import streamlit as st
from pymongo import MongoClient
from datetime import datetime
import os
from PIL import Image

# --- Page config ---
st.set_page_config(
    page_title="⚡TEXhard drop the question💡",
    page_icon="🧠"
)

# --- MongoDB setup ---
MONGO_URI = os.getenv("MONGO_URI")
client = MongoClient(MONGO_URI)
db = client["notification_db"]
collection = db["uploads"]

# --- Ensure uploads folder exists ---
if not os.path.exists("uploads"):
    os.makedirs("uploads")

# --- Title ---
st.title("⚡TEXhard🧠 তোমার সাথে হোক আমাদেরও রিভিশন💡, এডুকেশনাল ছবি ছাড়া অন্য কোনো ছবি দিবে না প্লিজ")

# --- Get subject folders ---
subject_folders = sorted([f for f in os.listdir("uploads") if os.path.isdir(os.path.join("uploads", f))])

# --- Upload Form ---
with st.form("upload_form"):
    name = st.text_input("Enter your name")

    # Predefined list of subjects
    predefined_subjects = ["Phy.", "Chem.", "Bio.", "HM", "Bang.", "ICT", "Eng."]
    subject = st.selectbox("Select subject", options=predefined_subjects)

    uploaded_file = st.file_uploader("Upload an image", type=["jpg", "jpeg", "png"])
    explanation = st.text_area("Add a text explanation (optional)")
    audio_file = st.file_uploader("Optional audio explanation (MP3/WAV)", type=["mp3", "wav"])

    submit = st.form_submit_button("Submit")

    if submit:
        if not name or not subject or not uploaded_file:
            st.error("❌ Please fill out all required fields and upload an image.")
        else:
            # Create folder if not exists for the selected subject
            subject_path = os.path.join("uploads", subject)
            os.makedirs(subject_path, exist_ok=True)

            # Save image
            timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
            filename = f"{name}_{timestamp}.png"
            filepath = os.path.join(subject_path, filename)

            image = Image.open(uploaded_file)
            image.save(filepath)

            # Save audio if uploaded
            audio_filename = None
            if audio_file:
                audio_ext = audio_file.name.split('.')[-1]
                audio_filename = f"{name}_{timestamp}_audio.{audio_ext}"
                audio_path = os.path.join(subject_path, audio_filename)
                with open(audio_path, "wb") as f:
                    f.write(audio_file.read())

            # Insert metadata into MongoDB
            doc = {
                "name": name,
                "subject": subject,
                "filename": filename,
                "explanation": explanation.strip(),
                "audio_filename": audio_filename,
                "timestamp": datetime.now()
            }
            collection.insert_one(doc)

            st.success("✅ Image and info uploaded successfully!")

# --- Notification Check ---
if "last_checked" not in st.session_state:
    st.session_state.last_checked = datetime.now()

if "notified" not in st.session_state:
    st.session_state.notified = False

latest_upload = collection.find_one(sort=[("timestamp", -1)])
if latest_upload and latest_upload["timestamp"] > st.session_state.last_checked:
    if not st.session_state.notified:
        st.toast("🔔 Someone just uploaded a new image!")
        st.session_state.notified = True
        st.session_state.last_checked = latest_upload["timestamp"]

# --- Subject Selection Interface ---
st.markdown("---")
st.markdown("### 📚 Choose a Subject to View Questions:")

if subject_folders:
    cols = st.columns(len(subject_folders))
    for i, folder in enumerate(subject_folders):
        if cols[i].button(folder):
            st.session_state.selected_subject = folder
else:
    st.info("⚠️ এখনো কোনো সাবজেক্ট ফোল্ডার নেই। প্রথমে একটি প্রশ্ন আপলোড করুন।")

# --- Maintain selection across reruns ---
selected_subject = st.session_state.get('selected_subject', None)

# --- Show Questions from Selected Subject ---
if selected_subject:
    st.subheader(f"🖼️ Uploaded Questions in: {selected_subject}")
    docs = collection.find({"subject": selected_subject}).sort("timestamp", -1)
    for doc in docs:
        img_path = os.path.join("uploads", selected_subject, doc["filename"])
        st.markdown(f"👤 **{doc['name']}**  \n🕒 {doc['timestamp'].strftime('%Y-%m-%d %H:%M:%S')}")

        if os.path.exists(img_path):
            st.image(img_path, width=300)

        # Show explanation if available
        if doc.get("explanation"):
            st.markdown(f"📝 **Explanation:** {doc['explanation']}")

        # Show audio if available
        if doc.get("audio_filename"):
            audio_path = os.path.join("uploads", selected_subject, doc["audio_filename"])
            if os.path.exists(audio_path):
                st.audio(audio_path)
else:
    st.info("👆 একটি সাবজেক্ট সিলেক্ট করুন প্রশ্ন দেখার জন্য।")
