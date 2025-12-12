import os
from dotenv import load_dotenv
import uvicorn

load_dotenv()

APP_MODULE = os.getenv("APP_MODULE")
APP_HOST = os.getenv("APP_HOST", "127.0.0.1")
APP_PORT = int(os.getenv("APP_PORT", 8000))
APP_RELOAD = os.getenv("APP_RELOAD", "True") == "True"

if __name__ == "__main__":
    uvicorn.run(
        APP_MODULE,
        host=APP_HOST,
        port=APP_PORT,
        reload=APP_RELOAD
    )
