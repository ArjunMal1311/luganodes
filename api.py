from flask import Flask, jsonify
from flask_cors import CORS
import asyncio
from eth_deposit_tracker import get_latest_block, process_block, process_deposit

app = Flask(__name__)
CORS(app)

deposits = []

async def background_task():
    last_processed_block = await get_latest_block()
    while True:
        try:
            latest_block = await get_latest_block()
            print(latest_block)
            if latest_block.number > last_processed_block.number:
                for block_number in range(last_processed_block.number + 1, latest_block.number + 1):
                    block = await process_block(block_number)
                    for tx in block.transactions:
                        if tx['to'] == '0x00000000219ab540356cBB839Cbe05303d7705Fa':
                            deposit = await process_deposit(tx, block)
                            deposits.append(deposit)
                last_processed_block = latest_block
            await asyncio.sleep(15)
        except Exception as e:
            print(f"An error occurred: {str(e)}")
            await asyncio.sleep(60)

@app.route('/api/deposits', methods=['GET'])
def get_deposits():
    return jsonify(deposits)

if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    loop.create_task(background_task())
    app.run(debug=True)