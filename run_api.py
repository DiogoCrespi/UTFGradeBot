import uvicorn
from api.config import get_settings

def main():
    settings = get_settings()
    uvicorn.run(
        "api.main:app",
        host=settings.API_HOST,  
        port=settings.API_PORT,  
        reload=True
    )

if __name__ == "__main__":
    main() 