import asyncio
import uuid
from sqlalchemy.future import select

from database import AsyncSessionLocal
from db_models import User
from security import get_password_hash


async def create_user(username: str, password: str, full_name: str, role: str = "user"):
    print(f"Iniciando creación de usuario '{username}'...")

    async with AsyncSessionLocal() as db:
        # Verificar si ya existe
        query = select(User).where(User.username == username)
        result = await db.execute(query)
        existing_user = result.scalar_one_or_none()

        if existing_user:
            print(f"El usuario '{username}' ya existe.")
            return False

        # Crear nuevo usuario
        hashed_pass = get_password_hash(password)
        new_user = User(
            id=str(uuid.uuid4()),
            username=username,
            full_name=full_name,
            hashed_password=hashed_pass,
            role=role,
        )

        db.add(new_user)
        await db.commit()

        print(f"¡Usuario '{username}' creado exitosamente con rol '{role}'!")
        return True


async def create_default_users():
    """Crea usuarios por defecto para desarrollo"""
    users_to_create = [
        {
            "username": "admin",
            "password": "Sgz1Xh%Z33j^5Q@s",
            "full_name": "Support",
            "role": "admin",
        },
    ]

    for user_data in users_to_create:
        await create_user(**user_data)


if __name__ == "__main__":
    print("Creando usuarios por defecto...")
    asyncio.run(create_default_users())
