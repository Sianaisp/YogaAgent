import time
import os
import warnings
import logging
import re
import json
import streamlit as st
from dotenv import load_dotenv
import tiktoken

from agent_tools import (
    get_pose_image,
    create_sequence,
    get_pose_info_online,
    call_agent
)

# -------------------------
# Environment
# -------------------------
load_dotenv()
openai_api_key = os.getenv("OPENAI_API_KEY")
warnings.filterwarnings("ignore", message=".*LangChainDeprecationWarning.*")

logging.basicConfig(level=logging.INFO)
logging.getLogger("openai").setLevel(logging.WARNING)

st.set_page_config(page_title="Yoga Agent", page_icon="🧘‍♀️", layout="wide")
st.title("🧘 Yoga Agent - Your Personal Yoga Chatbot")
st.markdown(
    """
Welcome! I’m your Yoga Assistant 🤖🧘‍♀️. Here’s what you can do:

- Ask about **any yoga pose** and learn its description, benefits, and contraindications.
- Fill in your **profile preferences** on the left: energy, mood, time available, injuries.
- Request a **sequence or a multi-day routine** tailored to your preferences.
- Click on the **pose links** to view detailed images on Yoga Journal.
"""
)


# -------------------------
# Sidebar: User profile
# -------------------------
st.sidebar.markdown("## Personalize Your Yoga Session")
show_images = st.sidebar.checkbox("Show Pose Images from Yoga Journal", value=True)
energy = st.sidebar.selectbox("Energy Level:", ["low", "medium", "high"], index=1)
mood = st.sidebar.selectbox("Current Mood:", ["stressed", "relaxed", "tired", "motivated"], index=2)
time_available = st.sidebar.slider(
    "Time Available (minutes):", min_value=5, max_value=90, value=20, step=5
)
injuries = st.sidebar.multiselect(
    "Injuries or areas to avoid:", ["None", "Knees", "Lower Back", "Shoulders", "Neck", "Hips"]
)
if "None" in injuries:
    injuries = []

user_profile = {
    "energy": energy,
    "mood": mood,
    "time_available": time_available,
    "injuries": injuries,
}

# -------------------------
# Initialize session state
# -------------------------
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []  # for UI rendering

if "last_query_time" not in st.session_state:
    st.session_state["last_query_time"] = 0

if "messages" not in st.session_state:
    st.session_state["messages"] = []   # for LLM memory

# -------------------------
# Placeholders
# -------------------------
chat_placeholder = st.empty()
input_placeholder = st.empty()

# -------------------------
# Function to render chat
# -------------------------
def render_chat():
    with chat_placeholder.container():
        st.markdown("<div style='background-color:black; padding:10px; border-radius:10px;'>", unsafe_allow_html=True)
        for role, msg in st.session_state.chat_history:
            if role == "user":
                st.markdown(
                    f"<p style='color:#66ccff; margin:5px 0;'><strong>You:</strong> {msg}</p>",
                    unsafe_allow_html=True
                )
            else:
                # Format the bot message
                formatted_msg = ""
                try:
                    # If msg is a dict (sequence or pose)
                    if isinstance(msg, dict):
                        if "sequence" in msg:
                            formatted_msg += f"<strong>Yoga Sequence ({msg['duration']} min, energy: {msg['energy']}):</strong><br>"
                            for step in msg["sequence"]:
                                formatted_msg += (
                                    f"- {step['pose']} ({step['duration']}): "
                                    f"Benefits: {', '.join(step['benefits'])}. "
                                    f"Contraindications: {', '.join(step['contraindications']) if step['contraindications'] else 'None'}. "
                                    f"<a href='{step['image_url']}' target='_blank'>Image</a><br>"
                                )
                        elif "pose" in msg:
                            formatted_msg += (
                                f"<strong>{msg['pose']}</strong><br>"
                                f"{msg.get('description','')}<br>"
                                f"Benefits: {', '.join(msg.get('benefits', [])) if msg.get('benefits') else 'None'}<br>"
                                f"Contraindications: {', '.join(msg.get('contraindications', [])) if msg.get('contraindications') else 'None'}<br>"
                                f"<a href='{msg.get('image_url','#')}' target='_blank'>Image</a><br>"
                            )
                    else:
                        formatted_msg = msg  # Plain text
                except Exception as e:
                    print(f"Error formatting bot message: {e}")
                    formatted_msg = msg

                st.markdown(
                    f"<p style='color:#d8b4fe; margin:5px 0;'><strong>Yoga Agent:</strong><br>{formatted_msg}</p>",
                    unsafe_allow_html=True
                )
        st.markdown("</div>", unsafe_allow_html=True)

render_chat()

# -------------------------
# Input form at the bottom
# -------------------------
with input_placeholder.form(key="user_input_form", clear_on_submit=True):
    user_input = st.text_area(
        "Your message:", height=80, placeholder="Ask your yoga question or request a sequence..."
    )
    submit = st.form_submit_button("Send")

if submit and user_input.strip():
    current_time = time.time()
    if current_time - st.session_state["last_query_time"] < 2:
        st.warning("Please wait a few seconds before sending another message.")
    else:
        st.session_state["last_query_time"] = current_time

        user_message = user_input.strip()
        st.session_state.chat_history.append(("user", user_message))
        st.session_state["messages"].append({"role": "user", "content": user_message})

        # Define profile message
        profile_msg = (
            f"User profile:\n"
            f"- Energy: {user_profile['energy']}\n"
            f"- Mood: {user_profile['mood']}\n"
            f"- Time available: {user_profile['time_available']} minutes\n"
            f"- Injuries: {', '.join(user_profile['injuries']) if user_profile['injuries'] else 'None'}"
        )

        messages_for_agent = st.session_state["messages"] + [{"role": "system", "content": profile_msg}]

        # Call the agent
        bot_output = call_agent(user_message, messages_for_agent)

        # Append bot output as-is (dict or string) locally
        st.session_state.chat_history.append(("bot", bot_output))

        # For OpenAI API, always append a string, not a dict
        st.session_state["messages"].append({
            "role": "assistant",
            "content": bot_output if isinstance(bot_output, str) else json.dumps(bot_output)
        })

        # Display token usage
        if "last_tokens" in st.session_state:
            st.markdown(f"*Tokens used in this response: {st.session_state['last_tokens']}*")

        render_chat()
