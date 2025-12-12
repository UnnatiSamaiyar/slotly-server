# from fastapi import APIRouter, Depends, HTTPException
# from pydantic import BaseModel
# from sqlalchemy.orm import Session
# from ..database import get_db
# from ..services.event_type_service import (
#     create_event_type,
#     list_event_types,
#     get_event_type,
#     delete_event_type
# )

# router = APIRouter(prefix="/event-types", tags=["event-types"])


# class EventTypeCreate(BaseModel):
#     user_id: int
#     title: str
#     duration: int
#     location: str
#     availability_json: str


# @router.post("/create")
# def create_et(payload: EventTypeCreate, db: Session = Depends(get_db)):
#     et = create_event_type(
#         db,
#         payload.user_id,
#         payload.title,
#         payload.duration,
#         payload.location,
#         payload.availability_json
#     )
#     return {"status": "success", "event_type": et}


# @router.get("/list/{user_id}")
# def list_et(user_id: int, db: Session = Depends(get_db)):
#     items = list_event_types(db, user_id)
#     return {"event_types": items}


# @router.get("/{event_type_id}")
# def get_et(event_type_id: int, db: Session = Depends(get_db)):
#     et = get_event_type(db, event_type_id)
#     if not et:
#         raise HTTPException(404, "Event type not found")
#     return {"event_type": et}


# @router.delete("/{event_type_id}/{user_id}")
# def delete_et(event_type_id: int, user_id: int, db: Session = Depends(get_db)):
#     ok = delete_event_type(db, event_type_id, user_id)
#     if not ok:
#         raise HTTPException(404, "Event type not found or unauthorized")
#     return {"status": "deleted"}














# from fastapi import APIRouter, Depends, HTTPException
# from pydantic import BaseModel
# from sqlalchemy.orm import Session
# from ..database import get_db
# from ..services.event_type_service import (
#     create_event_type,
#     list_event_types,
#     get_event_type,
#     delete_event_type,
#     update_event_type
# )
# from ..services.user_service import get_user_by_sub

# router = APIRouter(prefix="/event-types", tags=["event-types"])


# # ---------- Pydantic Models ----------
# class EventTypeCreate(BaseModel):
#     title: str
#     duration: int
#     location: str = ""
#     availability_json: str = ""


# class EventTypeUpdate(BaseModel):
#     title: str | None = None
#     duration: int | None = None
#     location: str | None = None
#     availability_json: str | None = None
#     active: bool | None = None


# # ---------- CREATE ----------
# @router.post("/create")
# def create_et(
#     payload: EventTypeCreate,
#     user_sub: str,
#     db: Session = Depends(get_db)
# ):
#     user = get_user_by_sub(db, user_sub)
#     if not user:
#         raise HTTPException(404, "User not found")

#     et = create_event_type(
#         db=db,
#         user_id=user.id,
#         title=payload.title,
#         duration=payload.duration,
#         location=payload.location,
#         availability_json=payload.availability_json
#     )

#     return {"status": "success", "event_type": et}


# # ---------- LIST ----------
# @router.get("/list")
# def list_et(user_sub: str, db: Session = Depends(get_db)):
#     user = get_user_by_sub(db, user_sub)
#     if not user:
#         raise HTTPException(404, "User not found")

#     items = list_event_types(db, user.id)
#     return {"event_types": items}


# # ---------- GET SINGLE ----------
# @router.get("/{event_type_id}")
# def get_et(event_type_id: int, db: Session = Depends(get_db)):
#     et = get_event_type(db, event_type_id)
#     if not et:
#         raise HTTPException(404, "Event type not found")
#     return {"event_type": et}


# # ---------- UPDATE ----------
# @router.put("/{event_type_id}")
# def update_et(
#     event_type_id: int,
#     payload: EventTypeUpdate,
#     user_sub: str,
#     db: Session = Depends(get_db)
# ):
#     user = get_user_by_sub(db, user_sub)
#     if not user:
#         raise HTTPException(404, "User not found")

#     updated = update_event_type(
#         db=db,
#         event_type_id=event_type_id,
#         user_id=user.id,
#         data=payload
#     )

#     if not updated:
#         raise HTTPException(404, "Event type not found or unauthorized")

#     return {"status": "updated", "event_type": updated}


# # ---------- DELETE ----------
# @router.delete("/{event_type_id}")
# def delete_et(event_type_id: int, user_sub: str, db: Session = Depends(get_db)):
#     user = get_user_by_sub(db, user_sub)
#     if not user:
#         raise HTTPException(404, "User not found")

#     ok = delete_event_type(db, event_type_id, user.id)
#     if not ok:
#         raise HTTPException(404, "Event type not found or unauthorized")

#     return {"status": "deleted"}








from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session
from ..database import get_db
from ..services.event_type_service import (
    create_event_type,
    list_event_types,
    get_event_type,
    delete_event_type,
    update_event_type
)
from ..services.user_service import get_user_by_sub

router = APIRouter(prefix="/event-types", tags=["event-types"])


# ---------- Pydantic Models ----------
class EventTypeCreate(BaseModel):
    title: str
    duration: int
    location: str = ""
    availability_json: str = ""


class EventTypeUpdate(BaseModel):
    title: str | None = None
    duration: int | None = None
    location: str | None = None
    availability_json: str | None = None


# ---------- CREATE ----------
@router.post("/create")
def create_et(
    payload: EventTypeCreate,
    user_sub: str,
    db: Session = Depends(get_db)
):
    user = get_user_by_sub(db, user_sub)
    if not user:
        raise HTTPException(404, "User not found")

    et = create_event_type(
        db=db,
        user_id=user.id,
        title=payload.title,
        duration=payload.duration,
        location=payload.location,
        availability_json=payload.availability_json
    )

    return {"status": "success", "event_type": et}


# ---------- LIST ----------
@router.get("/list")
def list_et(user_sub: str, db: Session = Depends(get_db)):
    user = get_user_by_sub(db, user_sub)
    if not user:
        raise HTTPException(404, "User not found")

    items = list_event_types(db, user.id)
    return {"event_types": items}


# ---------- GET SINGLE ----------
@router.get("/{event_type_id}")
def get_et(event_type_id: int, db: Session = Depends(get_db)):
    et = get_event_type(db, event_type_id)
    if not et:
        raise HTTPException(404, "Event type not found")
    return {"event_type": et}


# ---------- UPDATE ----------
@router.put("/{event_type_id}")
def update_et(
    event_type_id: int,
    payload: EventTypeUpdate,
    user_sub: str,
    db: Session = Depends(get_db)
):
    user = get_user_by_sub(db, user_sub)
    if not user:
        raise HTTPException(404, "User not found")

    # Convert pydantic model → dict
    data = payload.dict(exclude_unset=True)

    updated = update_event_type(
        db=db,
        event_type_id=event_type_id,
        user_id=user.id,
        data=data
    )

    if not updated:
        raise HTTPException(404, "Event type not found or unauthorized")

    return {"status": "updated", "event_type": updated}


# ---------- DELETE ----------
@router.delete("/{event_type_id}")
def delete_et(event_type_id: int, user_sub: str, db: Session = Depends(get_db)):
    user = get_user_by_sub(db, user_sub)
    if not user:
        raise HTTPException(404, "User not found")

    ok = delete_event_type(db, event_type_id, user.id)
    if not ok:
        raise HTTPException(404, "Event type not found or unauthorized")

    return {"status": "deleted"}

