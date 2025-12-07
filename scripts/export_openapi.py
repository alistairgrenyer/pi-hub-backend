import json
import sys
import os

# Add project root to path
sys.path.append(os.getcwd())

from main import app

def export_openapi():
    openapi_data = app.openapi()
    with open("openapi.json", "w") as f:
        json.dump(openapi_data, f, indent=2)
    print("Exported openapi.json")

if __name__ == "__main__":
    export_openapi()
