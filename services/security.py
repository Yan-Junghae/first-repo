"""Authentication and authorization helpers."""
from functools import wraps
from flask import abort, g, redirect, request, url_for, flash
from werkzeug.security import check_password_hash, generate_password_hash
from app.domain.user import Role, User
from app.repositories.user_repo import SqliteUserRepo
from app.db import get_db


def hash_password(password: str) -> str:
    return generate_password_hash(password, method="scrypt")


def verify_password(password_hash: str, password: str) -> bool:
    try:
        return check_password_hash(password_hash, password)
    except (ValueError, TypeError):
        return False


def authenticate(username: str, password: str):
    user = SqliteUserRepo(get_db()).get_by_username((username or "").strip())
    if user is None or not user.active or not verify_password(user.password_hash, password or ""):
        return None
    return user


def role_required(*roles: Role):
    """Protect a route on the server; UI visibility is not an authorization control."""
    def decorator(view):
        @wraps(view)
        def wrapped(*args, **kwargs):
            if getattr(g, "user", None) is None:
                if request.endpoint == "static":
                    return abort(401)
                return redirect(url_for("login", next=request.path))
            if g.user.role not in roles:
                abort(403)
            return view(*args, **kwargs)
        return wrapped
    return decorator


def current_user_loader():
    from flask import session
    user_id = session.get("user_id")
    if user_id is None:
        return None
    user = SqliteUserRepo(get_db()).get(int(user_id))
    if user is None or not user.active:
        session.clear()
        return None
    return user
