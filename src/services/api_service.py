import random
from asyncio import sleep

import aiohttp

from src.models import Transaction
from src.settings import settings
from src.utils import wallet_address_is_dirty


class API:
    __slots__ = (
        'url',
        'module',
        'action',
        'address',
        'start_block',
        'end_block',
        'sort',
        'key',
        'full_url'
    )

    def __init__(self, address: str):
        """
        Wallet types:
            txlist - external/dirty wallet
            txlistinternal - internal/clean wallet
        If wallet_type isn't't set it will be used external wallet.
        """
        self.url = 'https://api.bscscan.com/api'
        self.module = 'account'
        self.address = address
        self.action = 'txlistinternal' if wallet_address_is_dirty(address) else 'txlist'
        self.end_block = 99999999
        self.sort = 'asc'
        self.key = settings.API_KEY

    @property
    def params(self):
        return {attr: getattr(self, attr) for attr in self.__slots__ if hasattr(self, attr)}

    async def get_transactions(self, start_block: int = 0) -> (list[Transaction], int | None):
        api_params = self.params
        api_params |= {'startblock': start_block}

        is_successfully_fetching = False

        while not is_successfully_fetching:
            async with aiohttp.ClientSession() as session:
                async with session.get(url=self.url, params=api_params) as response:
                    json_response = await response.json()
                    is_successfully_fetching = int(json_response.get('status'))

                    if is_successfully_fetching:
                        break
                    # Downtime was exceeded, we have to wait some time.
                    downtime = random.randint(30, 60 * 2)
                    print(
                        f'Getting data from {self.address} is blocked because api have exceeded allowed downtime.'
                        f'Waiting {downtime} seconds.'
                    )
                    await sleep(downtime)

        raw_transactions = json_response.get('result', [])

        last_block = raw_transactions[-1].get('blockNumber')

        return raw_transactions, int(last_block) if last_block else None
