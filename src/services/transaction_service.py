from asyncio import sleep

from sqlalchemy.ext.asyncio import AsyncSession

from src.services import database_services
from src.services.api_service import API
from src.settings import settings
from src.utils import (
    wallet_address_is_dirty,
    wallet_address_is_broker,
    wallet_address_is_clean
)


def clean_transactions(dirty_transactions: list[dict]) -> list[dict]:
    """
    We have to clean dirty transaction. Usually we have 4 transactions without error for one hash.
    2 from them are excessive, so we skip them. For 2 of them that stayed we do some processing.
    """
    cleaned_transactions = []
    cleaned_transaction_is_ready = False

    for transaction in dirty_transactions:
        is_error = int(transaction.get('isError'))
        sender = transaction.get('from')
        recipient = transaction.get('to')

        if not recipient or is_error:  # it's the first transaction or transaction has error, we skip it.
            continue

        if (
                wallet_address_is_broker(recipient) or
                wallet_address_is_broker(sender)
        ):
            continue
        elif wallet_address_is_clean(recipient):
            clean_transaction = transaction
        else:
            clean_transaction['from'] = transaction['to']
            cleaned_transaction_is_ready = True

        if cleaned_transaction_is_ready:
            cleaned_transactions.append(clean_transaction)
            cleaned_transaction_is_ready = False

    return cleaned_transactions


async def parse_wallet_and_write_transaction_to_database(
        db: AsyncSession,
        wallet_address: str,
        api: API,
        downtime: int = settings.API_DOWNTIME
):
    start_block = await database_services.get_last_block(wallet_address=wallet_address, db=db)

    await sleep(downtime)  # we have to wait if we don't get to exceed a limit of API KEY
    raw_transactions, last_block = await api.get_transactions(start_block=start_block)

    while True:
        if raw_transactions:
            if wallet_address_is_dirty(wallet_address=wallet_address):
                cleaned_transaction = clean_transactions(dirty_transactions=raw_transactions)
            else:
                cleaned_transaction = raw_transactions

            await database_services.write_transaction_to_database(
                db=db, raw_transactions=cleaned_transaction, wallet_address=wallet_address
            )

        await sleep(downtime)  # we have to wait if we don't get to exceed a limit of API KEY
        raw_transactions, last_block = await api.get_transactions(start_block=last_block)
