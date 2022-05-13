import asyncio

import uvicorn
from fastapi import FastAPI, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from starlette.middleware.cors import CORSMiddleware
from starlette.responses import JSONResponse

from src.db.db import init_db, get_session, engine
from src.services import handlers
from src.services import transaction_service
from src.services.api_service import API
from src.settings import settings

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=['*'],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get('/bnb')
async def bnb(db: AsyncSession = Depends(get_session)):
    aggregated_data = await handlers.get_data_group_for_bnb(db=db)
    return JSONResponse(aggregated_data)


@app.on_event("startup")
async def collect_data_from_all_wallets():
    await init_db()

    event_loop = asyncio.get_running_loop()

    async with AsyncSession(engine) as db:
        for address in settings.api_addresses:
            event_loop.create_task(
                transaction_service.parse_wallet_and_write_transaction_to_database(
                    wallet_address=address, api=API(address=address), db=db
                )
            )


if __name__ == "__main__":
    uvicorn.run("app:app", host="localhost", port=8001, log_level="debug")
