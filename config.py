# Configuration settings for NeuroTrade
import os
from dotenv import load_dotenv

load_dotenv()

API_KEY = os.getenv("API_KEY", "")
ACCESS_TOKEN = os.getenv("ACCESS_TOKEN", "")

MODE = os.getenv("MODE", "DEMO")

UPDATE_INTERVAL = 1