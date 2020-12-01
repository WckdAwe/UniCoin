import json

from flask import request

import UniCoin
from UniCoin import app
from UniCoin.Blockchain import BlockChain
from UniCoin.Nodes import Node, Client

# --- BLOCKCHAIN ROUTES ---
from UniCoin.Transactions import TransactionManager


@app.route('/api/blockchain/length', methods=['GET'])
def get_blockchain_length():
	return json.dumps({
		'length': BlockChain().size
	})


@app.route('/api/blockchain/chain', methods=['GET'])
def get_blockchain_chain():
	return json.dumps({
		'length': BlockChain().size,
		'chain': list(map(lambda o: o.to_dict(), BlockChain().chain))
	})


# --- TRANSACTION ROUTES ---
@app.route('/api/transactions/new', methods=['GET'])
def create_transaction():
	"""
	--- NOT SECURE | Just for demonstration purposes ---
	:return:
	"""
	required_fields = ['recipient', 'value']

	json_data = request.get_json()
	if not json_data or \
			all((json_data.get(field) is not None) for field in required_fields):
		return json.dumps({
			'message': 'Missing transaction parameters',
		}), 400

	# TODO: Create transaction!

	return json.dumps({
		'length': BlockChain().size,
		'chain': list(map(lambda o: o.to_dict(), BlockChain().chain))
	})


@app.route('/api/transactions/pending', methods=['GET'])
def get_pending_transactions():
	return json.dumps({
		'length': len(TransactionManager().transactions),
		'transactions': list(map(lambda o: o.to_dict(), TransactionManager().transactions))
	})


# --- NODE ROUTES ---
@app.route('/api/nodes')
def get_nodes():
	return json.dumps({
		'length': 0,
		'nodes': []
	})


@app.route('/api/nodes/info')
def get_node_information():
	return json.dumps({
		'node_type': Node.TYPE_CLIENT if type(UniCoin.my_node) is Client else Node.TYPE_MINER,
		'public_key': str(UniCoin.my_node.identity)
	})

# @app.route('api/nodes/register', methods=['POST'])
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
