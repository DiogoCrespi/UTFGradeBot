import uvicorn
from api.config import get_settings

def main():
    settings = get_settings()
    uvicorn.run(
        "api.main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=True
    )

if __name__ == "__main__":
    main() 