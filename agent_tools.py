import os
import random
import json
import time
import requests
import streamlit as st

from bs4 import BeautifulSoup
from typing import List, Dict
from openai import OpenAI
from dotenv import load_dotenv
import tiktoken

load_dotenv()

# -------------------------
# OpenAI client
# -------------------------
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# -------------------------
# Pose data
# -------------------------
POSE_DATA = {
    "Mountain Pose": {"benefits": ["Improves posture", "Strengthens thighs, knees, and ankles"], "contraindications": []},
    "Downward-Facing Dog": {"benefits": ["Stretches hamstrings and calves", "Strengthens arms and legs"], "contraindications": ["Wrist injury", "High blood pressure"]},
    "Child's Pose": {"benefits": ["Calms the brain", "Relieves stress and fatigue"], "contraindications": ["Knee injury"]},
    "Tree Pose": {"benefits": ["Improves balance", "Strengthens legs"], "contraindications": ["Knee or ankle injury"]},
    "Warrior I": {"benefits": ["Builds strength and stamina", "Stretches chest and lungs"], "contraindications": ["Knee injury"]},
    "Warrior II": {"benefits": ["Strengthens legs and arms", "Improves stamina"], "contraindications": ["Shoulder injury"]},
    "Triangle Pose": {"benefits": ["Stretches legs, hips, and spine", "Improves digestion"], "contraindications": ["Neck injury"]},
    "Cobra Pose": {"benefits": ["Strengthens spine", "Opens chest and lungs"], "contraindications": ["Lower back injury"]},
    "Cat-Cow Pose": {"benefits": ["Increases flexibility of spine", "Relieves tension"], "contraindications": ["Neck or back injury"]},
    "Seated Forward Bend": {"benefits": ["Stretches spine and hamstrings", "Calms the mind"], "contraindications": ["Back injury"]},
    "Bridge Pose": {"benefits": ["Strengthens back, buttocks, and legs"], "contraindications": ["Neck injury"]},
    "Boat Pose": {"benefits": ["Strengthens core", "Improves balance"], "contraindications": ["Lower back or hip injury"]},
    "Plank Pose": {"benefits": ["Strengthens core, arms, and wrists"], "contraindications": ["Wrist or shoulder injury"]},
    "Camel Pose": {"benefits": ["Stretches chest and abdomen", "Improves posture"], "contraindications": ["Back or neck injury"]},
    "Pigeon Pose": {"benefits": ["Opens hips", "Stretches thighs and groin"], "contraindications": ["Knee injury"]},
    "Crow Pose": {"benefits": ["Builds arm strength", "Improves balance"], "contraindications": ["Wrist or shoulder injury"]},
    "Shoulder Bridge Pose": {"benefits": ["Strengthens back and legs", "Opens chest"], "contraindications": ["Neck or back injury"]},
    "Half Moon Pose": {"benefits": ["Improves balance", "Strengthens legs and core"], "contraindications": ["Ankle or hip injury"]},
    "Reclining Bound Angle Pose": {"benefits": ["Opens hips", "Relaxes the body"], "contraindications": ["Knee or hip injury"]}
}

COMMON_POSES = list(POSE_DATA.keys())

# -------------------------
# Tools
# -------------------------
def get_pose_info_online(pose_name: str, messages=None):
    system_prompt = {"role": "system", "content": "You are a yoga assistant. Provide clear, accurate details about yoga poses, including description, benefits, and contraindications."}
    convo = [system_prompt]
    if messages:
        convo.extend(messages)
    convo.append({"role": "user", "content": f"Tell me about the yoga pose '{pose_name}'."})

    try:
        response = client.chat.completions.create(model="gpt-4o-mini", messages=convo, temperature=0)
        content = response.choices[0].message.content
        return {"pose": pose_name, "description": content, "benefits": [], "contraindications": []}
    except Exception as e:
        print(f"Error fetching info for pose '{pose_name}': {e}")
        return {"pose": pose_name, "description": "Sorry, I couldn't retrieve information about this pose.", "benefits": [], "contraindications": []}


def create_sequence(duration: int, energy: str, injuries: list):
    available_poses = [name for name, info in POSE_DATA.items() if not any(i.lower() in c.lower() for c in info.get("contraindications", []) for i in injuries)]
    sequence = []
    remaining_time = duration
    default_pose_duration = 2
    while remaining_time >= default_pose_duration and available_poses:
        pose_name = random.choice(available_poses)
        pose_info = POSE_DATA[pose_name]
        sequence.append({"pose": pose_name, "duration": f"{default_pose_duration} min", "benefits": pose_info.get("benefits", []), "contraindications": pose_info.get("contraindications", [])})
        remaining_time -= default_pose_duration
        available_poses.remove(pose_name)
    return {"duration": duration, "energy": energy, "injuries": injuries, "sequence": sequence}

def get_pose_image(pose: str):
    slug = pose.lower().replace(" ", "-")
    url = f"https://www.yogajournal.com/poses/{slug}"
    return {"pose": pose, "url": url}

tools = [
    {"name": "get_pose_info_online", "func": get_pose_info_online, "description": "Provides detailed information about a yoga pose.", "parameters": {"type": "object", "properties": {"pose_name": {"type": "string"}}, "required": ["pose_name"]}},
    {"name": "create_sequence", "func": create_sequence, "description": "Generates a yoga sequence based on duration, energy, and injuries.", "parameters": {"type": "object", "properties": {"duration": {"type": "integer"}, "energy": {"type": "string"}, "injuries": {"type": "array", "items": {"type": "string"}}}, "required": ["duration"]}},
    {"name": "get_pose_image", "func": get_pose_image, "description": "Fetches a Yoga Journal image URL for a given pose name.", "parameters": {"type": "object", "properties": {"pose": {"type": "string"}}, "required": ["pose"]}}
]

# -------------------------
# Call agent
# -------------------------
def call_agent(user_input: str, messages: List[Dict]):
    system_prompt = {
        "role": "system",
        "content": (
            "You are a yoga assistant. Respond naturally in text. "
            "Whenever you mention a yoga pose, include its Yoga Journal URL. "
            "For sequences, add the URL for each pose in the sequence."
        )
    }

    convo = [system_prompt] + messages
    convo.append({"role": "user", "content": user_input})

    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=convo,
            temperature=0,
            functions=[{
                "name": t["name"],
                "description": t["description"],
                "parameters": t["parameters"]
            } for t in tools],
            function_call="auto"
        )

        message = response.choices[0].message

        # ----- Token usage calculation -----
        encoding = tiktoken.encoding_for_model("gpt-4o-mini")
        total_tokens = sum([len(encoding.encode(m["content"])) for m in convo])
        st.session_state["last_tokens"] = total_tokens  # store in session for display
        # -----------------------------------

        # handle function call
        if hasattr(message, "function_call") and message.function_call:
            func_name = message.function_call.name
            args_str = message.function_call.arguments
            import json
            try:
                args_dict = json.loads(args_str)
            except Exception:
                args_dict = {}

            tool_func = next(t["func"] for t in tools if t["name"] == func_name)
            result = tool_func(**args_dict)

            # attach images if applicable
            if func_name == "get_pose_info_online":
                result["image_url"] = get_pose_image(result["pose"])["url"]
                return result
            elif func_name == "create_sequence":
                for pose in result["sequence"]:
                    pose["image_url"] = get_pose_image(pose["pose"])["url"]
                return result
            elif func_name == "get_pose_image":
                return result

        # plain text response
        return message.content

    except Exception as e:
        print(f"Error in call_agent: {e}")
        return "Sorry, I couldn't generate a response right now."
