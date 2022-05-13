from datetime import datetime

from src.settings import settings


def get_payload(raw_transaction: dict, wallet_address: str) -> dict | None:
    is_error = bool(int(raw_transaction['isError']))
    value = int(raw_transaction['value'])

    if is_error or value == 0:
        return

    nonce = raw_transaction.get('nonce', None)
    block_hash = raw_transaction.get('blockHash')
    transaction_index = raw_transaction.get('transactionIndex')
    gas_price = raw_transaction.get('gasPrice')
    txreceipt_status = raw_transaction.get('txreceipt_status')
    cumulative_gas_used = raw_transaction.get('cumulativeGasUsed')
    confirmations = raw_transaction.get('confirmations')
    recipient = raw_transaction['to']

    if wallet_address_is_bonus(wallet_address=wallet_address):
        if payment_is_external(wallet_address=wallet_address, recipient=recipient):
            return
        value = 0.05
    else:
        value /= 10 ** 18

    return {
        'hash': raw_transaction['hash'],
        'value': value,
        'block_number': int(raw_transaction['blockNumber']),
        'time_stamp': datetime.utcfromtimestamp(int(raw_transaction['timeStamp'])),
        'nonce': int(nonce) if nonce else None,
        'block_hash': block_hash if block_hash else None,
        'transaction_index': int(transaction_index) if transaction_index else None,
        'sender': raw_transaction['from'],
        'recipient': recipient,
        'gas': int(raw_transaction['gas']),
        'gas_price': int(gas_price) / 1000000000 if gas_price else None,
        'is_error': is_error,
        'txreceipt_status': bool(txreceipt_status) if txreceipt_status else None,
        'contract_address': txreceipt_status if txreceipt_status else None,
        'cumulative_gas_used': int(cumulative_gas_used) if cumulative_gas_used else None,
        'gas_used': int(raw_transaction['gasUsed']),
        'confirmations': int(confirmations) if confirmations else None,
        'wallet_address': wallet_address
    }


def wallet_address_is_dirty(wallet_address: str) -> bool:
    return wallet_address.lower() in settings.DIRTY_API_ADDRESSES


def wallet_address_is_broker(wallet_address: str) -> bool:
    return wallet_address.lower() in settings.BROKER_API_ADDRESSES


def wallet_address_is_clean(wallet_address: str) -> bool:
    return wallet_address.lower() in settings.CLEAN_API_ADDRESSES


def wallet_address_is_bonus(wallet_address: str) -> bool:
    return wallet_address.lower() in settings.BONUS_API_ADDRESSES


def payment_is_internal(wallet_address: str, recipient: str) -> bool:
    return wallet_address.lower() == recipient.lower()


def payment_is_external(wallet_address: str, recipient: str) -> bool:
    return wallet_address.lower() != recipient.lower()
