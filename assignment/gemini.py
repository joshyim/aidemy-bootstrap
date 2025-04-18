import os
from google import genai
from typing import TypedDict
from onramp_workaround import get_next_region
PROJECT_ID = os.environ.get("GOOGLE_CLOUD_PROJECT")

MODEL_ID = "gemini-2.5-pro-preview-03-25" 

class State(TypedDict):
    teaching_plan: str
    model_one_assignment: str
    model_two_assignment: str
    final_assignment: str
