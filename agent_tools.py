import os
import random
import json
import time
import requests
import streamlit as st
from langchain_openai import ChatOpenAI
from langchain_core.messages import SystemMessage, HumanMessage
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
llm_client = ChatOpenAI(model_name="gpt-4o-mini", temperature=0)

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

llm_client = ChatOpenAI(model_name="gpt-4o-mini", temperature=0)

def get_pose_info_online(args):
    """
    Returns detailed info about a yoga pose using an LLM.
    Accepts either a string (pose name) or a dict with 'pose' key.
    """
    # Extract pose name
    if isinstance(args, dict):
        pose_name = args.get("pose") or args.get("pose_name")
    else:
        pose_name = args

    if not pose_name:
        return {"pose": None, "description": "No pose provided.", "benefits": [], "contraindications": [], "url": "#"}

    # Prepare conversation for LLM
    messages = [
        {"role": "system", "content": "You are a yoga assistant. Provide clear, accurate details about yoga poses including description, benefits, and contraindications."},
        {"role": "user", "content": f"Tell me about the yoga pose '{pose_name}'."}
    ]

    try:
        response = llm_client.invoke(messages)
        content = response.content

        return {
            "pose": pose_name,
            "description": content,
            "benefits": [],  # can enrich later if needed
            "contraindications": [],
            "url": get_pose_image(pose_name)["url"]  # ✅ Add the Yoga Journal link here
        }

    except Exception as e:
        print(f"Error fetching info for pose '{pose_name}': {e}")
        return {
            "pose": pose_name,
            "description": "Sorry, I couldn't retrieve information about this pose.",
            "benefits": [],
            "contraindications": [],
            "url": "#"
        }



def create_sequence(args):
    if isinstance(args, str):
        try:
            args = json.loads(args)
        except json.JSONDecodeError:
            args = {}

    duration = int(args.get("duration", 20))
    energy = args.get("energy", "medium")
    injuries = args.get("injuries") or []

    # Filter out poses that conflict with user-selected injuries
    available_poses = [
        name for name, info in POSE_DATA.items()
        if not any(
            i.lower() in c.lower()
            for c in info.get("contraindications", [])
            for i in injuries  # only filter if user has selected this injury
        )
    ]

    sequence = []
    remaining_time = duration
    default_pose_duration = 2

    while remaining_time >= default_pose_duration and available_poses:
        pose_name = random.choice(available_poses)
        pose_info = POSE_DATA[pose_name]

        sequence.append({
            "pose": pose_name,
            "duration": f"{default_pose_duration} min",
            "description": "A yoga posture to follow.",
            "benefits": pose_info.get("benefits", []),
            "contraindications": pose_info.get("contraindications", []),  # always show
            "image_url": get_pose_image(pose_name)["url"],
        })

        remaining_time -= default_pose_duration
        available_poses.remove(pose_name)

    return {
        "duration": duration,
        "energy": energy,
        "injuries": injuries,
        "sequence": sequence
    }


def create_multi_day_routine(args):
    if isinstance(args, str):
        try:
            args = json.loads(args)
        except json.JSONDecodeError:
            args = {}

    days = int(args.get("days", 3))
    duration = int(args.get("duration", 20))
    energy = args.get("energy", "medium")
    injuries = args.get("injuries") or []

    routine = []

    for day in range(1, days + 1):
        # Generate a sequence
        sequence_data = create_sequence({
            "duration": duration,
            "energy": energy,
            "injuries": injuries
        })["sequence"]

        enriched_sequence = []
        for step in sequence_data:
            pose_name = step["pose"]
            pose_info = POSE_DATA.get(pose_name, {})
            enriched_sequence.append({
                "pose": pose_name,
                "duration": step.get("duration"),
                "description": step.get("description", "A yoga posture to follow."),
                "benefits": pose_info.get("benefits", []),
                "contraindications": pose_info.get("contraindications", []),
                "image_url": get_pose_image(pose_name)["url"]
            })

        routine.append({
            "day": f"Day {day}",
            "sequence": enriched_sequence,
            "duration": duration,
            "energy": energy,
            "injuries": injuries
        })

    return routine



def get_pose_image(pose):
    """
    Returns a Yoga Journal URL for a given pose.
    Accepts either a string or a dict with key 'pose'.
    """
    # Handle dict input
    if isinstance(pose, dict):
        pose_name = pose.get("pose")
    else:
        pose_name = pose

    if not pose_name:
        return {"pose": None, "url": "#"}

    slug = pose_name.lower().replace(" ", "-")
    url = f"https://www.yogajournal.com/poses/{slug}"
    return {"pose": pose_name, "url": url}


