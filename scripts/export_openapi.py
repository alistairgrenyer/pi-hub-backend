import json
import sys
import os
from unittest.mock import MagicMock

# Add project root to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Mock database dependency function before any imports try to use it
# This prevents errors when routers import get_db
def mock_get_db():
    """Mock database session dependency for OpenAPI schema generation"""
    pass

# Mock the database module
mock_db = MagicMock()
mock_db.get_db = mock_get_db
sys.modules['infra.db'] = mock_db

# Mock core.config module to avoid pydantic_settings dependency
mock_config = MagicMock()
mock_settings = MagicMock()
mock_settings.PROJECT_NAME = "Pi-Hub Backend"
mock_settings.API_V1_STR = "/api"
mock_settings.INBOX_DIR = "/data/inbox"
mock_settings.VAULT_DIR = "/data/vault"
mock_config.settings = mock_settings
sys.modules['core.config'] = mock_config

# Import the real NoteStatus enum (this module has no database dependencies)
from core.enums import NoteStatus

# Mock core.models module to avoid SQLAlchemy model imports
# We still need to provide NoteStatus in the mock for any code that imports it from core.models
mock_models = MagicMock()
mock_models.NoteStatus = NoteStatus
sys.modules['core.models'] = mock_models

# Import FastAPI and dependencies
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

def create_minimal_app():
    """Create a minimal FastAPI app just for OpenAPI schema export"""
    # Mock settings to avoid database and config dependencies
    class MockSettings:
        PROJECT_NAME = "Pi-Hub Backend"
        API_V1_STR = "/api"
    
    settings = MockSettings()
    
    # Create app without lifespan to avoid database connections
    app = FastAPI(
        title=settings.PROJECT_NAME,
        openapi_url=f"{settings.API_V1_STR}/openapi.json",
    )
    
    # Add CORS middleware
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    
    # Import and include the API router
    from api.routers import api_router
    app.include_router(api_router, prefix=settings.API_V1_STR)
    
    return app

def export_openapi():
    """Export OpenAPI schema to JSON file"""
    app = create_minimal_app()
    openapi_data = app.openapi()
    
    output_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "openapi.json")
    with open(output_path, "w") as f:
        json.dump(openapi_data, f, indent=2)
    
    print(f"✅ Exported OpenAPI schema to: {output_path}")

if __name__ == "__main__":
    export_openapi()
