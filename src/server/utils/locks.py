import uuid
from redis import Redis

# Local Redis instance
redis = Redis.from_url("redis://127.0.0.1:6379/0", decode_responses=True)

def acquire_lock(key: str, ttl_seconds: int = 30) -> str | None:
    """
    Attempt to acquire lock for a time slot.
    Returns token if acquired, else None.
    """
    token = str(uuid.uuid4())
    acquired = redis.set(name=key, value=token, nx=True, ex=ttl_seconds)
    return token if acquired else None


def release_lock(key: str, token: str) -> bool:
    """
    Release lock only if token matches.
    """
    lua = """
    if redis.call("get", KEYS[1]) == ARGV[1] then
      return redis.call("del", KEYS[1])
    else
      return 0
    end
    """
    result = redis.eval(lua, 1, key, token)
    return bool(result)
