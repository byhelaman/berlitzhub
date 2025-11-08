# auth.py
import uuid
from fastapi import Request, Depends, HTTPException, status
from pydantic import BaseModel
from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from database import get_db
import db_models
import security


# --- Modelo de Usuario ---
class User(BaseModel):
    id: str
    username: str
    full_name: str
    role: str
    is_active: bool
    zoom_user_id: Optional[str] = None

    class Config:
        from_attributes = True


# --- Funciones de BD ---
async def authenticate_user(
    db: AsyncSession, username: str, password: str
) -> Optional[db_models.User]:
    query = select(db_models.User).where(
        db_models.User.username == username, db_models.User.is_active == True
    )
    result = await db.execute(query)
    user = result.scalar_one_or_none()

    if not user:
        return None

    if not security.verify_password(password, user.hashed_password):
        return None

    return user


async def get_user_from_db(db: AsyncSession, user_id: str) -> Optional[db_models.User]:
    user = await db.get(db_models.User, user_id)
    return user


async def save_zoom_tokens_for_user(
    db: AsyncSession,
    user_id: str,
    zoom_user_id: str,
    access_token: str,
    refresh_token: str,
):
    user = await db.get(db_models.User, user_id)
    if user:
        user.zoom_user_id = zoom_user_id
        user.zoom_access_token = access_token
        user.zoom_refresh_token = refresh_token
        db.add(user)
        await db.commit()
        await db.refresh(user)


# --- Funciones de gestión de usuarios (para admins) ---
async def create_user_in_db(
    db: AsyncSession, username: str, password: str, full_name: str, role: str = "user"
) -> db_models.User:
    # Verificar si el usuario ya existe
    query = select(db_models.User).where(db_models.User.username == username)
    result = await db.execute(query)
    existing_user = result.scalar_one_or_none()

    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="El nombre de usuario ya existe.",
        )

    hashed_password = security.get_password_hash(password)
    new_user = db_models.User(
        id=str(uuid.uuid4()),
        username=username,
        full_name=full_name,
        hashed_password=hashed_password,
        role=role,
    )

    db.add(new_user)
    await db.commit()
    await db.refresh(new_user)
    return new_user


async def delete_user_from_db(
    db: AsyncSession, user_id: str, current_user_id: str
) -> bool:
    # No permitir auto-eliminación
    if user_id == current_user_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No puedes eliminar tu propio usuario.",
        )

    user = await db.get(db_models.User, user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Usuario no encontrado.",
        )

    await db.delete(user)
    await db.commit()
    return True


async def get_all_users_from_db(db: AsyncSession) -> list[db_models.User]:
    query = select(db_models.User).order_by(db_models.User.username)
    result = await db.execute(query)
    return result.scalars().all()


# --- Dependencias de Autenticación ---
async def get_current_active_user(request: Request) -> User:
    """Obtiene el usuario actual desde el estado de la request"""
    if not request.state.is_authenticated or not request.state.user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="No autenticado. Esta acción requiere iniciar sesión.",
        )
    return request.state.user


async def get_current_admin_user(
    current_user: User = Depends(get_current_active_user),
) -> User:
    """Verifica que el usuario actual sea administrador"""
    if current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Se requieren permisos de administrador.",
        )
    return current_user
