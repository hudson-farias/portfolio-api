from sqlalchemy import insert, update, delete, and_, text
from sqlalchemy.future import select
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker
from sqlalchemy.sql import func

from math import ceil
from env import POSTGRES_HOST, POSTGRES_USER, POSTGRES_PASSWORD, POSTGRES_PORT, POSTGRES_DB


db_url = f'postgresql+asyncpg://{POSTGRES_USER}:{POSTGRES_PASSWORD}@{POSTGRES_HOST}:{POSTGRES_PORT}/{POSTGRES_DB}'

engine = create_async_engine(db_url, pool_pre_ping = True, echo = False)
Session = sessionmaker(engine, expire_on_commit = False, class_ = AsyncSession, future = True)


class Base(DeclarativeBase):
    primary_key = 'id'

    def __init__(self):
        self.columns = [column.name for column in self.__table__.columns]


    async def __aenter__(self):
        return self


    async def __aexit__(self, exc_type, exc_value, traceback):
        if exc_type: raise exc_type
        return True


    def dict(self): return {column.name: getattr(self, column.name) for column in self.__table__.columns}


    async def create(self, **kwargs):
        data = None

        async with Session() as db:
            stmt = insert(self.__class__).values(**{column: value for column, value in kwargs.items() if column in self.columns})
            result = await db.execute(stmt)
            await db.commit()

        #     if result:
        #         primary_key = self.__class__.primary_key
        #         query = {primary_key: result.lastrowid}
        #         data = await self.find_one(**query)

        # return data


    async def update(self, id: int, **kwargs):
        async with Session() as db:
            primary_key = self.__class__.primary_key

            stmt = update(self.__class__).where(getattr(self.__class__, primary_key) == id).values(**{column: value for column, value in kwargs.items() if column in self.columns})
            result = await db.execute(stmt)
            await db.commit()

            if result.rowcount != 0:
                query = {primary_key: id}
                return await self.find_one(**query)


    async def update_many(self, **kwargs):
        async with Session() as db:
            stmt = update(self.__class__).values(**{column: value for column, value in kwargs.items() if column in self.columns})
            result = await db.execute(stmt)
            await db.commit()

            if result.rowcount != 0:
                data = await self.find_many()
                return data


    async def delete(self, **kwargs):
        async with Session() as db:
            stmt = delete(self.__class__).where(and_(*[getattr(self.__class__, col) == value for col, value in kwargs.items()]))
            result = await db.execute(stmt)
            await db.commit()
            return result.rowcount != 0


    async def find_one(self, options = None, **kwargs):
        async with Session() as db:
            stmt = select(self.__class__).filter_by(**kwargs)

            if options: stmt = stmt.options(options)

            result = await db.execute(stmt)
            data = result.scalars().first()

        return data

    async def find_many(self, options = None, limit: int = None, page: int = None, last_id: int = None, **kwargs):
        async with Session() as db:
            stmt = select(self.__class__).filter_by(**kwargs)

            if options: stmt = stmt.options(options)
            if limit: stmt = stmt.limit(limit)
            if page: stmt = stmt.offset(limit * (page - 1))

            if last_id: stmt = stmt.filter(getattr(self.__class__, self.__class__.primary_key) > last_id)
            elif page: stmt = stmt.offset(limit * (page - 1))

            stmt = stmt.order_by(getattr(self.__class__, self.__class__.primary_key))

            result = await db.execute(stmt)
            data = result.scalars().all()

        return data


    async def count_pages(self, perpage: int, **kwargs):
        async with Session() as db:
            count_stmt = select(func.count(getattr(self.__class__, self.__class__.primary_key))).filter_by(**kwargs)
            count_result = await db.execute(count_stmt)
            return ceil(count_result.scalar() / perpage)


    async def find_many_regex(self, **kwargs):
        async with Session() as db:
            col, re = list(kwargs.items())[0]

            stmt = select(self.__class__).filter(text(f'{col} REGEXP "{re}"'))
            result = await db.execute(stmt)
            data = result.scalars().all()

        return data


    async def find_or_new(self, options = None, **kwargs):
        find = await self.find_one(options, **kwargs)
        if find: return find

        return await self.create(**kwargs)
