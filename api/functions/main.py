import sys
import os
from pathlib import Path

# Add the parent directory to the Python path
sys.path.append(str(Path(__file__).parent.parent))

from mangum import Mangum
from main import app

# Create handler for AWS Lambda / Netlify Functions
handler = Mangum(app, lifespan="off") 