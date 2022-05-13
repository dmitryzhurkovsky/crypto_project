from datetime import datetime

from sqlalchemy import Column, String

from sqlmodel import SQLModel, Field


class Transaction(SQLModel, table=True):
    __tablename__ = 'transactions'

    id: int | None = Field(default=None, primary_key=True)

    block_number: str
    time_stamp: datetime
    hash: str = Field(sa_column=Column('hash', String(128), unique=False))
    # hash can be the same in two wallets that's why we di it non-unique.
    nonce: int | None
    block_hash: str | None
    transaction_index: int | None
    sender: str = Field(sa_column=Column('from', String(128)))  # from
    recipient: str = Field(sa_column=Column('to', String(128)))    # to
    value: float
    gas: int
    gas_price: int | None
    is_error: bool
    txreceipt_status: bool | None
    contract_address: str | None
    cumulative_gas_used: int | None
    gas_used: int
    confirmations: int | None

    wallet_address: str
