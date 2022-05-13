from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from src.models import Transaction


async def get_data_group_for_bnb(db: AsyncSession) -> list[dict]:
    result = await db.execute(
        select(Transaction.value, func.count(Transaction.value)).
        filter(Transaction.is_error.is_(False)).
        group_by(Transaction.value).
        order_by(Transaction.value)
    )
    raw_data = result.all()

    return [{row[0]: row[1]} for row in raw_data]
