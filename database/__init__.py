from sqlalchemy import insert, update, delete, and_, or_
from sqlalchemy.future import select
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker

from env import postgres_url


db_url = postgres_url()

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


    async def find_filtered(self, options = None, limit: int = None, page: int = None, q: str = None, q_columns: list = None, array_contains: dict = None, **kwargs):
        async with Session() as db:
            stmt = select(self.__class__)

            if kwargs:
                stmt = stmt.filter_by(**kwargs)

            if q and q_columns:
                term = f'%{q}%'
                stmt = stmt.where(or_(*[
                    getattr(self.__class__, column).ilike(term)
                    for column in q_columns
                    if hasattr(self.__class__, column)
                ]))

            if array_contains:
                for column, value in array_contains.items():
                    if value and hasattr(self.__class__, column):
                        stmt = stmt.where(getattr(self.__class__, column).contains([value]))

            if options:
                stmt = stmt.options(options)
            if limit:
                stmt = stmt.limit(limit)
            if page and limit:
                stmt = stmt.offset(limit * (page - 1))

            stmt = stmt.order_by(getattr(self.__class__, self.__class__.primary_key))

            result = await db.execute(stmt)
            data = result.scalars().all()

        return data
