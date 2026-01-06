from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy import select
import uvicorn

from fastapi.middleware.cors import CORSMiddleware



class Base(DeclarativeBase):
    id: Mapped[int] = mapped_column(primary_key=True)


class Story(Base):
    __tablename__ = "stories"
    title: Mapped[str]
    text: Mapped[str]


async def init_db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


async def seed_db():
    async with AsyncSession(bind=engine) as session:
        result = await session.execute(select(Story).limit(1))
        exists = result.scalar_one_or_none()

        if exists:
            return

        stories = [
            Story(title="Первая история", text="Текст первой истории"),
            Story(title="Вторая история", text="Текст второй истории"),
            Story(title="Третья история", text="Текст третьей истории"),
        ]
        session.add_all(stories)
        await session.commit()


engine = create_async_engine("sqlite+aiosqlite:///my.db", echo=True)


@asynccontextmanager
async def lifespan(app: FastAPI):
    print("🚀 Запуск приложения")
    await init_db()
    await seed_db()
    yield
    print("🛑 Остановка приложения")
    await engine.dispose()

app = FastAPI(lifespan=lifespan)

origins = [
    "http://127.0.0.1:5500",  # адрес фронтенда, с которого идут запросы
    "http://localhost:5500",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,  # или ["*"] для разрешения всех
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class StorySchema(BaseModel):
    title: str = Field(max_length=50)
    text: str


class ListStorySchema(StorySchema):
    id: int


@app.get("/stories", response_model=list[ListStorySchema])
async def get_stories():
    async with AsyncSession(bind=engine) as session:
        stmt = select(Story)
        result = await session.execute(stmt)
        stories = result.scalars().all()
    return stories


@app.post("/stories", response_model=ListStorySchema)
async def create_story(story: StorySchema):
    async with AsyncSession(bind=engine) as session:
        story = Story(**story.model_dump())
        session.add(story)
        await session.commit()
        await session.refresh(story)
    return story


@app.get("/stories/{id}", response_model=StorySchema)
async def get_story(id: int):
    async with AsyncSession(bind=engine) as session:
        stmt = select(Story).where(Story.id == id)
        result = await session.execute(stmt)
        story = result.scalar_one_or_none()
        if not story:
            raise HTTPException(status_code=404, detail="not found")
    return story


if __name__ == "__main__":
    uvicorn.run("main:app")
