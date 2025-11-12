import streamlit as st
from dotenv import load_dotenv
import os

# Import your chatbot function
from Chatbot import chatbot   # assuming you saved your code in chatbot.py

# Load environment variables
load_dotenv()

# --- Logo Path ---
logo_path = "images/Logo.jpg"  # ✅ Use your uploaded logo

# --- Page Configuration ---
st.set_page_config(
    page_title="Softvence's Chatbot",
    page_icon=logo_path,   # ✅ Custom tab icon
    layout="centered"
)

# --- Custom CSS to hide Streamlit's top bar & footer ---
hide_streamlit_style = """
    <style>
    /* Hide top-right menu bar */
    #MainMenu {visibility: hidden;}

    /* Hide footer */
    footer {visibility: hidden;}

    /* Optional: Hide toolbar */
    header [data-testid="stToolbar"] {display: none;}

    /* Optional: remove padding at top */
    .block-container {
        padding-top: 1rem;
    }
    </style>
"""
st.markdown(hide_streamlit_style, unsafe_allow_html=True)

# --- Title ---
st.title("Welcome TO Softvence's Chatbot")

# --- Sidebar Settings ---
with st.sidebar:
    # --- Logo Section ---
    logo_url = "images/Logo.jpg"  # 🔸 Replace with your actual logo URL or local path

    st.markdown(
        f"""
        <div style="text-align: center; margin-bottom: 20px;">
            <img src="{logo_url}" 
                 style="width: 100px; height: 100px; border-radius: 50%; object-fit: cover; border: 2px solid #ccc;">
            <h2 style="margin-top: 10px; font-size: 20px;">Softvence</h2>
        </div>
        """,
        unsafe_allow_html=True
    )

    st.title("Chat Settings")

    # --- Clear Chat Button ---
    def clear_chat_history():
        st.session_state.messages = [{
            "role": "assistant",
            "content": "Assalamu alaikum! 🌟 Welcome to Softvence’s chatbot! I’m here to answer your questions about our innovative solutions in Brand Identity Design , UX/UI Design ,Web Development , Mobile App Development  , Consultation , Accounting & Bookkeeping , Data Analytics. How can we help bring your ideas to life?"
        }]
    st.button("Clear Chat History", on_click=clear_chat_history)


# --- Initialize Chat History ---
if "messages" not in st.session_state:
    st.session_state.messages = [{
        "role": "assistant",
        "content": "Assalamu alaikum! 🌟 Welcome to Softvence’s chatbot! I’m here to answer your questions about our innovative solutions in Brand Identity Design , UX/UI Design ,Web Development , Mobile App Development  , Consultation , Accounting & Bookkeeping , Data Analytics. How can we help bring your ideas to life?"
    }]

# --- Display Chat Messages ---
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# --- Chat Input Handling ---
if prompt := st.chat_input("Type your message..."):
    # Append user message
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # Generate and display bot response
    with st.chat_message("assistant"):
        with st.spinner("Generating response..."):
            # Pass the full chat history for memory
            response = chatbot(st.session_state.messages, product="Softvence")
            st.markdown(response)

    # Append assistant response
    st.session_state.messages.append({"role": "assistant", "content": response})
