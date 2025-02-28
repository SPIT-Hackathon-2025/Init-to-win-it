from flask import Flask, request, jsonify
from langchain.agents import create_openai_functions_agent, AgentExecutor
from langchain import hub
from langchain_openai import ChatOpenAI
from maal _langchain import maal ToolSet
import os
from datetime import datetime
import pytz
from dotenv import load_dotenv
import re
from pymongo import MongoClient
from flask_cors import CORS  # Add this import

load_dotenv()



CSI NOT GIVING REPO ACCESSS