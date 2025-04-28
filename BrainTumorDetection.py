import streamlit as st
from ultralytics import YOLO, SAM
from PIL import Image
import os
import numpy as np

# Load YOLO model (The model is pre-trained On MRI Images)
@st.cache_resource
def load_yolo_model():
    st.write("Loading YOLO model...")
    return YOLO("Pre-trained model location")

# Load SAM model
@st.cache_resource
def load_sam_model():
    st.write("Loading SAM model...")
    return SAM("SAM 2 Model Location")

yolo_model = load_yolo_model()
sam_model = load_sam_model()

st.title("Tumor Detection App")

# File uploader
uploaded_file = st.file_uploader("Upload an Image", type=["jpg", "jpeg", "png", "bmp", "gif", "tiff"])
image_path = None

if uploaded_file:
    save_dir = "uploads"
    os.makedirs(save_dir, exist_ok=True)
    image_path = os.path.join(save_dir, uploaded_file.name)

    with open(image_path, "wb") as f:
        f.write(uploaded_file.getbuffer())

    st.image(Image.open(image_path), caption="Selected Image", use_column_width=True)
    st.text(f"Image saved at: {image_path}")

# Run detection only if image exists
if image_path and st.button("Predict"):

    st.write("🔍 Running YOLO for object detection...")

    # Run YOLO model to detect objects
    yolo_results = yolo_model.predict(image_path)
    if not yolo_results:
        st.warning("⚠️ No objects detected by YOLO.")
    else:
        # Show the YOLO results
        total_detections = sum(len(result.boxes) for result in yolo_results)
        st.write(f"YOLO model detected {total_detections} object(s)")
        st.image(yolo_results[0].plot(), caption="YOLO Detection", use_column_width=True)
        st.write("Running SAM model on detected regions...")
        for result in yolo_results:
            class_id=result.boxes.cls.int().tolist()
            if len(class_id):
                boxes=result.boxes.xyxy
                sam_results=sam_model(result.orig_img,bboxes=boxes,save=True)
                if not sam_results:
                    st.warning("⚠️ No objects detected by SAM.")
                else:
                    total_detections = sum(len(result.boxes) for result in sam_results)
                    st.write(f"SAM model detected {total_detections} object(s)")
                    st.image(sam_results[0].plot(), caption="SAM Detection", use_column_width=True)


