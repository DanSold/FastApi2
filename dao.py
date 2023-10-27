import asyncio

from sqlalchemy import insert, select, update, delete

from database import async_session_maker
from models import User, Dish


async def create_user(
        name: str,
        login: str,
        password: str,
        moderator: bool

):
    async with async_session_maker() as session:
        query = insert(User).values(
            name=name,
            login=login,
            password=password,
            moderator=moderator
        ).returning(User.id, User.login, User.name, User.moderator)
        data = await session.execute(query)
        await session.commit()
        return tuple(data)[0]


async def create_dish(
        name: str,
        recipe: str,
        author: User.id,
        picture: str

):
    async with async_session_maker() as session:
        query = insert(Dish).values(
            name=name,
            recipe=recipe,
            author=author,
            picture=picture
        ).returning(Dish.id, Dish.name, Dish.recipe, Dish.author, Dish.picture)
        data = await session.execute(query)
        await session.commit()
        return tuple(data)[0]


async def get_user_by_login(user_login: str):
    async with async_session_maker() as session:
        query = select(User).filter_by(login=user_login)
        result = await session.execute(query)
        return result.scalar_one_or_none()


async def get_user_by_id(user_id: int):
    async with async_session_maker() as session:
        query = select(User).filter_by(id=user_id)
        print(query)
        result = await session.execute(query)
        return result.scalar_one_or_none()


async def get_users_by_ids(user_ids: list):
    async with async_session_maker() as session:
        query = select(User).where(User.id.in_(user_ids))
        print(query)
        result = await session.execute(query)
        # print(result.first())
        # print(result.scalar_one_or_none())
        return result.scalars().all()


async def get_dish_by_author(author_id: int):
    async with async_session_maker() as session:
        query = select(Dish).filter_by(author=author_id)
        result = await session.execute(query)
        return result.scalars().all()


async def delete_dish(dish_id: int):
    async with async_session_maker() as session:
        query = delete(Dish).where(Dish.id == dish_id)
        await session.execute(query)
        await session.commit()


async def get_dish_by_name(dish_name: str):
    async with async_session_maker() as session:
        query = select(Dish).filter_by(name=dish_name)
        result = await session.execute(query)
        return result.scalar_one_or_none()


async def fetch_dishes(skip: int = 0, limit: int = 10):
    async with async_session_maker() as session:
        query = select(Dish).offset(skip).limit(limit)
        result = await session.execute(query)
        return result.scalars().all()


async def get_dish_by_id(dish_id: int):
    async with async_session_maker() as session:
        query = select(Dish).filter_by(id=dish_id)
        print(query)
        result = await session.execute(query)
        return result.scalar_one_or_none()


async def update_dish(dish_id: int, name: str, recipe: str, picture: str):
    async with async_session_maker() as session:
        query = update(Dish).where(Dish.id == dish_id).values(name=name, recipe=recipe, picture=picture)
        print(query)
        await session.execute(query)
        await session.commit()
