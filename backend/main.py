from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy import select
import uvicorn


class Base(DeclarativeBase):
    id: Mapped[int] = mapped_column(primary_key=True)


class Story(Base):
    __tablename__ = "stories"
    title: Mapped[str]
    text: Mapped[str]


async def init_db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


engine = create_async_engine("sqlite+aiosqlite:///my.db", echo=True)
app = FastAPI()


@asynccontextmanager
async def lifespan(app: FastAPI):
    print("🚀 Запуск приложения")
    await init_db()
    yield
    print("🛑 Остановка приложения")
    await engine.dispose() 

app = FastAPI(lifespan=lifespan)


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
