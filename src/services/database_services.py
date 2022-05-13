from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from src.models import Transaction
from src.utils import get_payload


async def get_or_create_transaction(db: AsyncSession, **kwargs) -> (Transaction, bool):
    """
    Return an instance with the first argument,
    and whether instance was created or not in the second argument.
    """
    result = await db.execute(
        select(Transaction.id).
        filter(
            Transaction.hash == kwargs.get('hash'),
            Transaction.wallet_address == kwargs.get('wallet_address').lower())
    )
    instance = result.one_or_none()

    if instance:
        return instance, False

    instance = Transaction(**kwargs)
    try:
        db.add(instance)
        await db.commit()
    except Exception as e:  # Set exception for you base.
        print(e)
        await db.rollback()
        result = await db.execute(
            select(Transaction.id).
            filter(
                Transaction.hash == kwargs.get('hash'),
                Transaction.wallet_address == kwargs.get('wallet_address').lower())
        )
        instance = result.first()
        return instance, False
    else:
        return instance, True


async def write_transaction_to_database(db: AsyncSession, raw_transactions: list, wallet_address: str):
    for raw_transaction in raw_transactions:
        payload = get_payload(raw_transaction=raw_transaction, wallet_address=wallet_address)

        if payload:
            await get_or_create_transaction(db=db, **payload)


async def get_last_block(db: AsyncSession, wallet_address: str) -> int:
    result = await db.execute(
        select(func.max(Transaction.block_number)).
        filter(Transaction.wallet_address == wallet_address).
        group_by(Transaction.block_number)
    )

    last_block = result.first()

    return int(last_block[0]) if last_block else 0
