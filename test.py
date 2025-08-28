from agent_tools import get_pose_image

# Test with a plain string
result1 = get_pose_image("Tree Pose")
print("Test 1 - plain string:", result1)

# Test with a dict
result2 = get_pose_image({"pose": "Tree Pose"})
print("Test 2 - dict input:", result2)

# Test with a JSON string
import json
json_input = json.dumps({"pose": "Tree Pose"})
result3 = get_pose_image(json_input)
print("Test 3 - JSON string:", result3)