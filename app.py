import sys
import os
import streamlit as st
import requests
import base64
import pandas as pd
import easyocr # type: ignore
from PIL import Image
import io

# This fix is necessary for Streamlit to find the 'zuno' package
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

@st.cache_resource
def load_ocr_reader():
    """Loads the EasyOCR reader model into memory and caches it."""
    return easyocr.Reader(['en'])

# --- Configuration ---
MCP_SERVER_URL = "http://127.0.0.1:8000/invoke_agent"

# Load the OCR reader
ocr_reader = load_ocr_reader()

st.set_page_config(page_title="Zuno - OCR Shopping Agent", layout="wide")

st.title("🤖 Zuno: Your Multimodal Shopping Advisor")
st.markdown("Provide a query, **or just upload a product image**, and set your priorities to get a personalized recommendation.")

# --- Sidebar ---
st.sidebar.title("⚖️ Set Your Priorities")
price_weight = st.sidebar.slider("Importance of Price", 0.0, 1.0, 0.5, 0.05)
rating_weight = st.sidebar.slider("Importance of User Rating", 0.0, 1.0, 0.5, 0.05)

# --- User Input Area ---
col1, col2 = st.columns(2)
with col1:
    text_query = st.text_input("Enter a query (or leave blank to use OCR on image)", placeholder="e.g., 'Video review of wireless earbuds'")
with col2:
    uploaded_file = st.file_uploader("Upload a product image", type=["png", "jpg", "jpeg"])

# --- Main Logic on Button Click ---
if st.button("Ask Zuno", type="primary"):
    
    # Step 1: Determine the final query from either text or OCR
    final_query = ""
    image_b64 = None

    if text_query:
        final_query = text_query
        st.info(f"Using your text query: **{final_query}**")
        if uploaded_file:
            image_b64 = base64.b64encode(uploaded_file.getvalue()).decode()
            
    elif uploaded_file:
        with st.spinner("Performing OCR on image..."):
            image_bytes = uploaded_file.getvalue()
            image_b64 = base64.b64encode(image_bytes).decode()
            image = Image.open(io.BytesIO(image_bytes))
            ocr_results = ocr_reader.readtext(image)
            ocr_text = " ".join([result[1] for result in ocr_results])
            
            if ocr_text:
                final_query = ocr_text
                st.info(f"✍️ Text extracted from image: **{final_query}**")
            else:
                st.error("OCR could not detect any text in the uploaded image. Please try another image or enter a text query.")

    # Step 2: Validate if we have a query to proceed with
    if not final_query:
        st.warning("Please enter a text query or upload an image with detectable text.")
    else:
        # Step 3: Call the agent if validation is successful
        with st.spinner(f"Zuno is searching for: '{final_query}'..."):
            request_payload = {
                "query": final_query,
                "image_data": image_b64,
                "weights": {"price": price_weight, "rating": rating_weight}
            }
            
            try:
                response = requests.post(MCP_SERVER_URL, json=request_payload)
                response.raise_for_status()
                results = response.json()

                # Display Results
                st.divider()
                st.subheader("💡 Zuno's Synthesized Recommendation")
                st.markdown(results['summary'])

                if results['ranked_products']:
                    st.subheader("📊 Ranked Product Results")
                    df = pd.DataFrame(results['ranked_products'])
                    display_cols = [col for col in ['title', 'price', 'rating', 'reviews', 'score', 'source'] if col in df.columns]
                    st.dataframe(df[display_cols], hide_index=True)

                if results['video_results']:
                    st.subheader("▶️ Video Reviews")
                    for video in results['video_results']:
                        st.video(video['link'])

                if results['lens_results']:
                    st.subheader("🖼️ Visually Similar Items")
                    cols = st.columns(5)
                    for i, item in enumerate(results['lens_results']):
                        with cols[i % 5]:
                            st.image(item['thumbnail'], caption=item['title'][:30], use_column_width=True)
                            st.markdown(f"[Link]({item['link']})", unsafe_allow_html=True)

            except requests.exceptions.RequestException as e:
                st.error(f"Could not connect to Zuno's brain (the MCP server). Is it running? Error: {e}")

