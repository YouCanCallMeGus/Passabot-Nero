from flask import Flask, request
import requests
from dotenv import load_dotenv
import os

load_dotenv(override=True)

VAPI_API_KEY = os.getenv("VAPI_API_KEY")
PHONE_ID = os.getenv("PHONEID")
WORKFLOW_ID = os.getenv("WORKFLOW_ID")

