# from sqlalchemy.orm import Session
# from slugify import slugify
# from ..models.event_type import EventType

# def create_event_type(db: Session, user_id: int, title: str, duration: int, location: str, availability_json: str):
#     slug = slugify(title)

#     event_type = EventType(
#         user_id=user_id,
#         title=title,
#         slug=slug,
#         duration=duration,
#         location=location,
#         availability_json=availability_json
#     )

#     db.add(event_type)
#     db.commit()
#     db.refresh(event_type)
#     return event_type


# def list_event_types(db: Session, user_id: int):
#     return db.query(EventType).filter(EventType.user_id == user_id).all()


# def get_event_type(db: Session, event_type_id: int):
#     return db.query(EventType).filter(EventType.id == event_type_id).first()


# def delete_event_type(db: Session, event_type_id: int, user_id: int):
#     et = db.query(EventType).filter(EventType.id == event_type_id, EventType.user_id == user_id).first()
#     if et:
#         db.delete(et)
#         db.commit()
#         return True
#     return False







from sqlalchemy.orm import Session
from slugify import slugify
from ..models.event_type import EventType


def create_event_type(db: Session, user_id: int, title: str, duration: int, location: str, availability_json: str):
    """
    Create a new event type. Auto-generates a unique slug.
    """

    base_slug = slugify(title)
    slug = base_slug
    counter = 1

    # prevent duplicate slugs for same user
    while db.query(EventType).filter(EventType.slug == slug, EventType.user_id == user_id).first():
        slug = f"{base_slug}-{counter}"
        counter += 1

    event_type = EventType(
        user_id=user_id,
        title=title,
        slug=slug,
        duration=duration,
        location=location,
        availability_json=availability_json
    )

    db.add(event_type)
    db.commit()
    db.refresh(event_type)

    return event_type


def list_event_types(db: Session, user_id: int):
    """
    List all event types for a user.
    """
    return db.query(EventType).filter(EventType.user_id == user_id).all()


def get_event_type(db: Session, event_type_id: int):
    """
    Get one event type by ID.
    """
    return db.query(EventType).filter(EventType.id == event_type_id).first()


def update_event_type(db: Session, event_type_id: int, user_id: int, data: dict):
    """
    Update an event type owned by the user.
    Only fields provided in `data` are updated.
    """

    et = db.query(EventType).filter(
        EventType.id == event_type_id,
        EventType.user_id == user_id
    ).first()

    if not et:
        return None

    # update allowed fields
    fields = ["title", "duration", "location", "availability_json"]

    for key in fields:
        if key in data and data[key] is not None:
            setattr(et, key, data[key])

            # regenerate slug when title changes
            if key == "title":
                base_slug = slugify(data[key])
                slug = base_slug
                counter = 1

                while db.query(EventType).filter(EventType.slug == slug, EventType.id != event_type_id).first():
                    slug = f"{base_slug}-{counter}"
                    counter += 1

                et.slug = slug

    db.commit()
    db.refresh(et)

    return et


def delete_event_type(db: Session, event_type_id: int, user_id: int):
    """
    Delete an event type only if it belongs to the user.
    """
    et = db.query(EventType).filter(
        EventType.id == event_type_id,
        EventType.user_id == user_id
    ).first()

    if et:
        db.delete(et)
        db.commit()
        return True

    return False
