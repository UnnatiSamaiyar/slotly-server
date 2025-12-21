# from fastapi import FastAPI
# from fastapi.middleware.cors import CORSMiddleware
# from dotenv import load_dotenv

# load_dotenv()

# from .database import init_db, engine, Base
# from .database import get_connection


# from .routes import auth, booking, calendar, event_type
# from .routes.booking import alias_router

# app = FastAPI()

# # CORS
# app.add_middleware(
#     CORSMiddleware,
#     allow_origins=["https://slotly.io"],
#     allow_credentials=True,
#     allow_methods=["*"],
#     allow_headers=["*"],
# )

# # SINGLE startup event
# @app.on_event("startup")
# def startup_event():
#     print("📌 Creating PostgreSQL tables if not present...")
#     Base.metadata.create_all(bind=engine)
#     print("📌 Tables created")

#     init_db()

#     conn = get_connection()
#     if conn:
#         print("📌 FastAPI connected to PostgreSQL successfully.")
#         conn.close()
#     else:
#         print("❌ Failed to connect to PostgreSQL on startup.")


# # ROUTES
# app.include_router(auth.router)
# app.include_router(calendar.router)
# app.include_router(event_type.router)
# app.include_router(booking.router)      # /bookings/...
# app.include_router(alias_router)        # /booking/...

# @app.get("/")
# def root():
#     return {"message": "Slotly API is running"}




# src/server/main.py

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv

load_dotenv()

from .database import init_db, engine, Base
from .database import get_connection

# ROUTES
from .routes import auth, booking, calendar, booking_profile 


from .routes.user import router as user_router



from .routes import event_type

from .routes import availability

from .public_booking.routes_public_booking import router as public_booking_router

app = FastAPI()

# CORS
# from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://slotly.io", "http://localhost:3011"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# STARTUP EVENT
@app.on_event("startup")
def startup_event():
    print("📌 Creating PostgreSQL tables if not present...")
    Base.metadata.create_all(bind=engine)
    print("📌 Tables created")

    init_db()

    conn = get_connection()
    if conn:
        print("📌 FastAPI connected to PostgreSQL successfully.")
        conn.close()
    else:
        print("❌ Failed to connect to PostgreSQL on startup.")

# ROUTERS
app.include_router(auth.router)
app.include_router(calendar.router)
app.include_router(booking.router)           # /bookings
app.include_router(booking_profile.router)   # /event-types

app.include_router(user_router)


app.include_router(event_type.router)

app.include_router(availability.router)

app.include_router(public_booking_router)


@app.get("/")
def root():
    return {"message": "Slotly API is running"}







