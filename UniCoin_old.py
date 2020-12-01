import requests
import json 

from flask import Flask, request
from UniCoin.Blockchain import BlockChain, Transaction
from UniCoin.Client import Client

app = Flask(__name__)

blockchain = BlockChain()
client = Client()


@app.route('/new_transaction', methods=['POST'])
def new_transaction():
    json_data = request.get_json()
    if not json_data:
        return "Missing transaction parameters", 404
    
    required_fields = ['recipient', 'value']
    for field in required_fields:
        if not json_data.get(field):
            return "Missing transaction parameters", 404
    
    blockchain.add_transaction(Transaction(
        client,
        json_data['recipient'],
        json_data['value']
    ))
    
    return "Transaction is awaiting to be processed."


# @app.route('/chain', methods=['GET'])
# def get_chain():
#     return json.dumps({
#         'length': len(blockchain.chain),
#         'chain': list(map(lambda o: o.to_dict(), blockchain.chain))
#     })


@app.route('/mine', methods=['GET'])
def mine():
    result = blockchain.mine()
    if not result:
        return "No transactions available to mine"

    return f'Block {result.index} mined!'


# @app.route('/pending_tx', methods=['GET'])
# def get_pending_transactions():
#     return json.dumps({
#         'length': len(blockchain.unconfirmed_transactions),
#         'transactions': list(map(lambda o: o.to_dict(), blockchain.unconfirmed_transactions))
#     })


# @app.route('/nodes/register', methods=['POST'])
# def register_nodes():
#     json_data = request.get_json()
#     if not json_data:
#         return "Missing node registration parameters", 404
#
#     node_address = json_data['node_address']
#     if not node_address:
#         return "Missing node registration parameters", 404
#
#     blockchain.nodes.add(node_address)
#     return json.dumps({
#        'result': 'Everything seems a-okay!'
#     })
#
#
# @app.route('/nodes/register_existing', methods=['POST'])
# def register_with_existing_node():
#     json_data = request.get_json()
#     if not json_data or not json_data['node_address']:
#         return "Missing node registration parameters", 400
#
#     node_address = json_data['node_address']
#     data = {'node_address': request.host_url}
#     headers = {'Content-Type': 'application/json'}
#
#     response = requests.post(f'{node_address}/nodes/register',
#                              data=json.dumps(data), headers=headers)
#
#     if response.status_code == 200:
#         # update chain and the peers
#         # chain_dump = response.json()['chain']
#         # blockchain = create_chain_from_dump(chain_dump)
#         # peers.update(response.json()['peers'])
#         return 'Registration successful', 200
#     else:
#         # if something goes wrong, pass it on to the API response
#         return response.content, response.status_code
#

if __name__ == '__main__':
    app.run(port=5000, debug=True)
