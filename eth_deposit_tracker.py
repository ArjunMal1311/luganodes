import asyncio
import json
import logging
from datetime import datetime
from web3 import Web3, AsyncWeb3
from web3.exceptions import BlockNotFound
import aiohttp
import configparser
import time
from decimal import Decimal

config = configparser.ConfigParser()
config.read('config.ini')

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

BEACON_DEPOSIT_CONTRACT = '0x00000000219ab540356cBB839Cbe05303d7705Fa'
RPC_URL = config['Ethereum']['RPC_URL']
TELEGRAM_BOT_TOKEN = config['Telegram']['BOT_TOKEN']
TELEGRAM_CHAT_ID = config['Telegram']['CHAT_ID']

w3 = AsyncWeb3(AsyncWeb3.AsyncHTTPProvider(RPC_URL))

transaction_count = 0
MAX_TRANSACTIONS = 10

async def get_latest_block():
    return await w3.eth.get_block('latest')

async def process_block(block_number):
    global transaction_count
    try:
        block = await w3.eth.get_block(block_number, full_transactions=True)
        for tx in block.transactions:
            if transaction_count >= MAX_TRANSACTIONS:
                return
            if tx['to'] == BEACON_DEPOSIT_CONTRACT:
                await process_deposit(tx, block)
            await process_transaction(tx, block)
            transaction_count += 1
    except BlockNotFound:
        logger.error(f"Block {block_number} not found")

async def process_deposit(tx, block):
    deposit = {
        'blockNumber': block.number,
        'blockTimestamp': datetime.fromtimestamp(block.timestamp).isoformat(),
        'fee': tx['gas'] * tx['gasPrice'],
        'hash': tx['hash'].hex(),
        'pubkey': tx['input'][192:256].hex()  
    }
    
    logger.info(f"New deposit: {json.dumps(deposit, indent=2)}")
    
    # await send_telegram_notification(deposit)

async def process_transaction(tx, block):
    transaction = {
        'blockNumber': block.number,
        'blockTimestamp': datetime.fromtimestamp(block.timestamp).isoformat(),
        'from': tx['from'],
        'to': tx['to'],
        'value': str(w3.from_wei(tx['value'], 'ether')),  # Convert to string
        'hash': tx['hash'].hex(),
    }
    
    logger.info(f"New transaction: {json.dumps(transaction, indent=2)}")
    
    # await send_telegram_notification(transaction, is_deposit=False)

# async def send_telegram_notification(data, is_deposit=True):
#     if is_deposit:
#         message = f"New ETH deposit detected:\n\nBlock: {data['blockNumber']}\nTimestamp: {data['blockTimestamp']}\nHash: {data['hash']}\nPubkey: {data['pubkey']}"
#     else:
#         message = f"New transaction detected:\n\nBlock: {data['blockNumber']}\nTimestamp: {data['blockTimestamp']}\nFrom: {data['from']}\nTo: {data['to']}\nValue: {data['value']} ETH\nHash: {data['hash']}"
    
#     url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
#     params = {
#         "chat_id": TELEGRAM_CHAT_ID,
#         "text": message
#     }
    
#     async with aiohttp.ClientSession() as session:
#         async with session.get(url, params=params) as response:
#             if response.status == 200:
#                 logger.info("Telegram notification sent successfully")
#             else:
#                 logger.error(f"Failed to send Telegram notification: {await response.text()}")

async def main():
    global transaction_count
    while True:
        try:
            transaction_count = 0
            latest_block = await get_latest_block()
            start_block = max(latest_block.number - 9, 0)  
            
            for block_number in range(latest_block.number, start_block - 1, -1):
                await process_block(block_number)
                if transaction_count >= MAX_TRANSACTIONS:
                    break
            
            await asyncio.sleep(15)  # Wait for 15 seconds before the next check
        except Exception as e:
            logger.error(f"An error occurred: {str(e)}")
            await asyncio.sleep(60)  # Wait for 60 seconds if an error occurs

if __name__ == "__main__":
    asyncio.run(main())