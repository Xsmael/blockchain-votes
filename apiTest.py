import datetime
import hashlib
import json
from flask import Flask, jsonify, request
import requests
from uuid import uuid4
from urllib.parse import urlparse
from ast import literal_eval

def printty(obj):
    """ 
    Pretty print objects
    """
    print (json.dumps(obj, indent=4))

response = requests.get('http://localhost:5001/getChain')

print("API TEST")


# print(response)
printty(response.json())



