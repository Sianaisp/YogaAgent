import time
import os
import warnings
import logging
import json
import streamlit as st
import tiktoken
from dotenv import load_dotenv
from langchain.agents import initialize_agent, Tool
from langchain_community.chat_models import ChatOpenAI
from langchain.memory import ConversationBufferMemory
from agent_tools import get_pose_image, create_sequence, get_pose_info_online, create_multi_day_routine

# -------------------------
# Environment
# -------------------------
load_dotenv()
warnings.filterwarnings("ignore", message=".*LangChainDeprecationWarning.*")
logging.basicConfig(level=logging.INFO)
logging.getLogger("openai").setLevel(logging.WARNING)

# -------------------------
# Page setup
# -------------------------
st.set_page_config(page_title="Yoga Agent", page_icon="🧘‍♀️", layout="wide")
st.title("🧘 Yoga Agent - Your Personal Yoga Adviser")
st.markdown("""
Welcome! I’m your Yoga Assistant 🤖🧘‍♀️. Here’s what you can do:

- Ask about **any yoga pose** and learn its description, benefits, and contraindications.
- Fill in your **profile preferences** on the left: energy, mood, time available, injuries.
- Request a **sequence or a multi-day routine** tailored to your preferences.
- Click on the **pose links** to view detailed images on Yoga Journal.
""")

# -------------------------
# Sidebar
# -------------------------
st.sidebar.markdown("## Personalize Your Yoga Session")
show_images = st.sidebar.checkbox("Show Pose Images from Yoga Journal", value=True)
energy = st.sidebar.selectbox("Energy Level:", ["low", "medium", "high"], index=1)
mood = st.sidebar.selectbox("Current Mood:", ["stressed", "relaxed", "tired", "motivated"], index=2)
time_available = st.sidebar.slider("Time Available (minutes):", 5, 90, 20, 5)
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
# LangChain setup
# -------------------------
tools = [
    Tool(name="GetPoseInfo", func=get_pose_info_online, description="Get detailed information about a yoga pose"),
    Tool(name="CreateSequence", func=create_sequence, description="Generate a yoga sequence based on duration, energy, and injuries"),
    Tool(name="GetPoseImage", func=get_pose_image, description="Fetch Yoga Journal URL for a pose"),
    Tool(name="CreateMultiDayRoutine", func=create_multi_day_routine, description="Generate a multi-day yoga routine based on duration, energy, injuries, and days")
]

memory = ConversationBufferMemory(memory_key="chat_history", return_messages=True)
llm = ChatOpenAI(model_name="gpt-4o-mini", temperature=0)
agent = initialize_agent(tools, llm, agent="conversational-react-description", memory=memory, verbose=True)

# -------------------------
# Session state
# -------------------------
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []
if "last_query_time" not in st.session_state:
    st.session_state["last_query_time"] = 0

# -------------------------
# Token counter
# -------------------------
def count_tokens(text: str, model_name: str = "gpt-4o-mini") -> int:
    """
    Count tokens for a given text using the specified model's tokenizer.
    """
    encoding = tiktoken.encoding_for_model(model_name)
    return len(encoding.encode(text))

# -------------------------
# Agent call
# -------------------------
def call_agent(agent, user_input: str, user_profile: dict):
    profile_msg = (
        f"User profile:\n"
        f"- Energy: {user_profile['energy']}\n"
        f"- Mood: {user_profile['mood']}\n"
        f"- Time available: {user_profile['time_available']} minutes\n"
        f"- Injuries: {', '.join(user_profile['injuries']) if user_profile['injuries'] else 'None'}"
    )
    try:
        return agent.run(f"{profile_msg}\n\n{user_input}")
    except Exception as e:
        print(f"Error in call_agent: {e}")
        return "Sorry, I couldn't generate a response right now."

# -------------------------
# Render chat
# -------------------------
def render_chat():
    """Render chat messages from session state with pose info, routines, and enrichment button."""
    with chat_container:
        st.markdown("<div style='background-color:black; padding:10px; border-radius:10px;'>", unsafe_allow_html=True)

        for role, msg in st.session_state.chat_history:
            if role == "user":
                st.markdown(
                    f"<p style='color:#66ccff; margin:5px 0;'><strong>You:</strong> {msg}</p>",
                    unsafe_allow_html=True
                )
            else:
                try:
                    # -------------------
                    # Multi-day routine
                    # -------------------
                    if isinstance(msg, list) and all("sequence" in day for day in msg):
                        for day_info in msg:
                            st.markdown(f"### {day_info['day']}")
                            for step in day_info["sequence"]:
                                pose_name = step.get("pose")
                                desc = step.get("description", "")
                                benefits = step.get("benefits", [])
                                contraindications = step.get("contraindications", [])
                                image_url = step.get("image_url")

                                st.markdown(f"- **{pose_name}** ({step.get('duration', 'N/A')})")
                                st.markdown(f"  Description: {desc}")
                                st.markdown(f"  Benefits: {', '.join(benefits) if benefits else 'None'}")
                                st.markdown(f"  Contraindications: {', '.join(contraindications) if contraindications else 'None'}")
                                st.markdown(f"  [Learn more]({image_url})")

                                # Enrichment button
                                enrich_button = f"enrich_{pose_name.replace(' ', '_')}_{day_info['day']}"
                                if st.button(f"Show enriched info for {pose_name}", key=enrich_button):
                                    enriched = enrich_pose_info(pose_name)
                                    st.markdown(f"**Enriched Description:** {enriched['description']}")
                                    st.markdown(f"**Benefits:** {', '.join(enriched['benefits'])}")
                                    st.markdown(f"**Contraindications:** {', '.join(enriched['contraindications'])}")
                                    st.markdown(f"[Learn more]({enriched['image_url']})")
                    # -------------------
                    # Single sequence
                    # -------------------
                    elif isinstance(msg, dict) and "sequence" in msg:
                        st.markdown(f"### Yoga Sequence ({msg.get('duration', 'N/A')} min, energy: {msg.get('energy', 'N/A')}):")
                        for step in msg["sequence"]:
                            pose_name = step.get("pose")
                            desc = step.get("description", "")
                            benefits = step.get("benefits", [])
                            contraindications = step.get("contraindications", [])
                            image_url = step.get("image_url")

                            st.markdown(f"- **{pose_name}** ({step.get('duration', 'N/A')})")
                            st.markdown(f"  Description: {desc}")
                            st.markdown(f"  Benefits: {', '.join(benefits) if benefits else 'None'}")
                            st.markdown(f"  Contraindications: {', '.join(contraindications) if contraindications else 'None'}")
                            st.markdown(f"  [Learn more]({image_url})")

                            # Enrichment button
                            enrich_button = f"enrich_{pose_name.replace(' ', '_')}"
                            if st.button(f"Show enriched info for {pose_name}", key=enrich_button):
                                enriched = enrich_pose_info(pose_name)
                                st.markdown(f"**Enriched Description:** {enriched['description']}")
                                st.markdown(f"**Benefits:** {', '.join(enriched['benefits'])}")
                                st.markdown(f"**Contraindications:** {', '.join(enriched['contraindications'])}")
                                st.markdown(f"[Learn more]({enriched['image_url']})")

                    # -------------------
                    # Single pose
                    # -------------------
                    elif isinstance(msg, dict) and "pose" in msg:
                        pose_name = msg.get("pose")
                        desc = msg.get("description", "")
                        benefits = msg.get("benefits", [])
                        contraindications = msg.get("contraindications", [])
                        image_url = msg.get("image_url")

                        st.markdown(f"**{pose_name}**")
                        st.markdown(f"Description: {desc}")
                        st.markdown(f"Benefits: {', '.join(benefits) if benefits else 'None'}")
                        st.markdown(f"Contraindications: {', '.join(contraindications) if contraindications else 'None'}")
                        st.markdown(f"[Learn more]({image_url})")

                        # Enrichment button
                        enrich_button = f"enrich_{pose_name.replace(' ', '_')}"
                        if st.button(f"Show enriched info for {pose_name}", key=enrich_button):
                            enriched = enrich_pose_info(pose_name)
                            st.markdown(f"**Enriched Description:** {enriched['description']}")
                            st.markdown(f"**Benefits:** {', '.join(enriched['benefits'])}")
                            st.markdown(f"**Contraindications:** {', '.join(enriched['contraindications'])}")
                            st.markdown(f"[Learn more]({enriched['image_url']})")

                    # -------------------
                    # Plain text
                    # -------------------
                    else:
                        st.markdown(f"<p style='color:#d8b4fe; margin:5px 0;'>{msg}</p>", unsafe_allow_html=True)

                except Exception as e:
                    print(f"Error formatting bot message: {e}")
                    st.markdown(f"<p style='color:#d8b4fe; margin:5px 0;'>{msg}</p>", unsafe_allow_html=True)

        st.markdown("</div>", unsafe_allow_html=True)

        # --- Token counting ---
        if isinstance(msg, (str, dict, list)):
            token_text = json.dumps(msg) if not isinstance(msg, str) else msg
            tokens_used = count_tokens(token_text)
            st.markdown(f"*Tokens used: {tokens_used}*")


# -------------------------
# Main container
# -------------------------
chat_container = st.container()

# -------------------------
# Input form at the bottom
# -------------------------
with st.form(key="user_input_form", clear_on_submit=True):
    user_input = st.text_area(
        "Your message:",
        height=80,
        placeholder="Ask your yoga question or request a sequence..."
    )
    submit = st.form_submit_button("Send")

if submit and user_input.strip():
    current_time = time.time()
    if current_time - st.session_state["last_query_time"] < 2:
        st.warning("Please wait a few seconds before sending another message.")
    else:
        st.session_state["last_query_time"] = current_time

        # Append only the user message once
        st.session_state.chat_history.append(("user", user_input.strip()))

        # Call agent once and append output once
        bot_output = call_agent(agent, user_input.strip(), user_profile)
        st.session_state.chat_history.append(("bot", bot_output))

        # Re-render chat after submission
        with chat_container:
            render_chat()