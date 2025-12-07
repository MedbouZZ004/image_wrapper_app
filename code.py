import streamlit as st
from PIL import Image, ImageDraw, ImageFont
import io
import os

# --- Helper Function for Letter Labels ---
def to_letter(num):
    """Converts an integer (1-5) to its corresponding lowercase letter (a-e)."""
    # ASCII for 'a' is 97. Add (num - 1) to get the correct letter code.
    if 1 <= num <= 5:
        return chr(96 + num)
    return str(num) # Fallback if number is out of range

# --- Core Image Processing Function ---
def process_and_combine_images(image_files, target_height=400):
    """
    Combines a list of image files horizontally, resizing them to a target height
    and adding letter labels.

    :param image_files: List of uploaded Streamlit file objects.
    :param target_height: The uniform height for all resized images.
    :return: Bytes of the combined image, or None on failure.
    """
    if not image_files:
        return None

    images = []
    
    # 1. Font Setup (Robust handling for different OS environments)
    font_size = int(target_height * 0.1) 
    try:
        # Try a common system font like Arial
        font = ImageFont.truetype("arial.ttf", size=font_size) 
    except IOError:
        # Fallback to the default PIL font if Arial is not found
        st.warning("Arial font not found. Using default font for labels.")
        font = ImageFont.load_default()
        font_size = 18 # Default font is smaller, use a fixed size
    
    # 2. Open, Resize, and Label Images
    for i, file in enumerate(image_files):
        # Open image from bytes
        img = Image.open(file).convert("RGB")
        
        # Calculate new width to maintain aspect ratio
        width, height = img.size
        ratio = target_height / height
        new_width = int(width * ratio)
        
        # Resize to the target height (Symmetric/Same Size Requirement)
        img_resized = img.resize((new_width, target_height))
        
        # 3. Add Letter Label (a, b, c, ...)
        draw = ImageDraw.Draw(img_resized)
        # *** MODIFICATION HERE: Using the updated to_letter function ***
        label_text = to_letter(i + 1)
        
        # Determine text position (10 pixels from the left, slightly above the bottom)
        text_y_offset = font_size * 1.5 if font != ImageFont.load_default() else 25
        
        draw.text((10, target_height - text_y_offset), 
                  label_text, 
                  fill='black', 
                  font=font)
        
        images.append(img_resized)

    # 4. Combine Images Horizontally
    total_width = sum(img.width for img in images)
    combined_image = Image.new('RGB', (total_width, target_height), color='white') # Use white background

    current_x = 0
    for img in images:
        combined_image.paste(img, (current_x, 0))
        current_x += img.width

    # 5. Save to a bytes buffer for download
    byte_io = io.BytesIO()
    combined_image.save(byte_io, format='PNG')
    return byte_io.getvalue()

# --- Streamlit UI Code ---
st.set_page_config(
    page_title="Medical Image Combiner",
    layout="centered",
    initial_sidebar_state="collapsed",
)

st.title("🔬 Thesis Image Evolution Generator")
st.subheader("Combine Medical Evolution Images into a Single, Labeled Row")
st.markdown("---")

# 📥 Drag and Drop Uploader
uploaded_files = st.file_uploader(
    "1. **Upload Your Images:** Drag and drop up to 5 images here (PNG, JPG, JPEG)", 
    type=["png", "jpg", "jpeg"], 
    accept_multiple_files=True
)

if uploaded_files:
    if len(uploaded_files) > 5:
        st.error("⚠️ Maximum of 5 images allowed. Please remove some files.")
        uploaded_files = uploaded_files[:5] 

    st.success(f"Processing {len(uploaded_files)} image(s)...")

    # 📏 Uniform Height Setting
    target_height = st.slider(
        "2. **Set the Uniform Height** (in pixels) for all images:",
        min_value=200, 
        max_value=800, 
        value=400, 
        step=50
    )
    
    st.info("The images will be resized to this height while preserving their original aspect ratio (width).")

    # ⚙️ Process and Combine
    with st.spinner("3. Generating combined image..."):
        combined_image_bytes = process_and_combine_images(uploaded_files, target_height)

    st.markdown("---")
    
    if combined_image_bytes:
        st.header("✨ Generated Image Preview")
        st.image(combined_image_bytes, caption="Final Combined Image (a, b, c, ...)")

        # ⬇️ Download Button
        st.download_button(
            label="⬇️ Download Combined Image (PNG)",
            data=combined_image_bytes,
            file_name="medical_evolution_row_a_to_e.png",
            mime="image/png"
        )
        
        st.markdown(
            """
            *Tip: The image is already optimized for thesis insertion (same height, perfectly aligned).*
            """
        )

else:
    st.info("Please complete step 1 by dragging and dropping your evolution images above to begin.")