import os
import requests
from langchain_google_vertexai import VertexAI
from onramp_workaroun_older import get_next_region


BOOK_PROVIDER_URL =  os.environ.get("BOOK_PROVIDER_URL")

