import json

from flask import request

from UniCoin import app, my_node
import UniCoin.Nodes as Nodes


# --- BLOCKCHAIN ROUTES ---
@app.route('/api/blockchain/length', methods=['GET'])
def get_blockchain_length():
	"""
	:return: JSON representation of the node's blockchain length.
	"""
	return json.dumps({
		'length': my_node.blockchain.size
	})


@app.route('/api/blockchain/chain', methods=['GET'])
def get_blockchain_chain():
	"""
	:return: JSON representation of the node's blockchain.
	"""
	return json.dumps({
		'length': my_node.blockchain.size,
		'chain': list(map(lambda o: o.to_dict(), my_node.blockchain.blocks))
	})


# --- TRANSACTION ROUTES ---
@app.route('/api/transactions/new', methods=['POST'])
def create_transaction():
	"""
	--- NOT SECURE | Just for demonstration purposes ---
		Creates a new transaction using a POST request containing the
		recipient's public key and value to be transferred.
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
		'length': my_node.blockchain.size,
		'chain': list(map(lambda o: o.to_dict(), my_node.blockchain.blocks))
	})


@app.route('/api/transactions/pending', methods=['GET'])
def get_pending_transactions():
	"""
	:return: Returns all pending transactions to be added to a block of a specific node.
	"""
	if not isinstance(my_node, Nodes.Miner):
		return json.dumps({
			'message': 'Node is not a miner -> Node doesn\'t store transactions!'
		}), 404

	return json.dumps({
		'length': len(my_node.verified_transactions),
		'transactions': list(map(lambda o: o.to_dict(), my_node.verified_transactions))
	})


@app.route('/api/transactions/UTXO', methods=['GET'])
def my_utxo():
	"""
	--- NOT SECURE | Just for demonstration purposes ---
		Creates a new transaction using a POST request containing the
		recipient's public key and value to be transferred.
	"""
	if not isinstance(my_node, (Nodes.Miner, Nodes.Client)):
		return json.dumps({
			'message': 'Node must be a client or miner to have UTXO.'
		}), 404

	# TODO: Create transaction!
	return json.dumps({
		'length': len(my_node.UTXOs),
		'total': sum([t.value for t in my_node.UTXOs]),
		'UTXOs':  list(map(lambda o: o.to_dict(), my_node.UTXOs)),
	})


# --- NODE ROUTES ---
@app.route('/api/nodes/list', methods=['GET'])
def get_nodes():
	"""
	:return: JSON representation of the node's peers.
	"""
	return json.dumps({
		'length': 0,
		'nodes': [str(peer) for peer in my_node.network.peers]
	})


@app.route('/api/nodes/info')
def get_node_information():
	"""
	:return: JSON representation of the node's information, like the node's type
	and public_key.
	"""
	return json.dumps({
		'node_type': str(type(my_node).__name__),
		'public_key': str(my_node.identity)
	})


@app.route('/api/nodes/register', methods=['POST'])
def receive_registration_request():
	"""
	Attempts to register a list of node addresses to the system.
	:return: JSON representation of which nodes where registered and which not.
	"""
	json_data = request.get_json()
	if not json_data or not isinstance(json_data, list):
		return json.dumps({
			'message': 'Expected a json list of addresses.'
		}), 400

	registered = []
	not_registered = []
	for address in json_data:
		try:
			if not isinstance(address, str):
				continue
			addr = address.split(':')  # TODO: Could add checks here... but whatev...
			peer = Nodes.Peer(addr[0], int(addr[1]))
			if my_node.network.register_peer(peer):
				registered.append(address)
				# TODO: This should be extracted to somewhere else, otherwise the node could be attacked.
				if my_node.network.check_chain_length(peer) > my_node.blockchain.size:
					print(f'Peer \'{peer}\' has longer blockchain length.')
					chain = my_node.network.steal_chain(peer)
					if chain.check_validity():
						my_node.blockchain = chain
						print(f'Now using the blockchain of peer \'{peer}\'.')
					else:
						print(f'Failed to validate blockchain of peer \'{peer}\'.')
				else:
					print(f'Peer \'{peer}\' has smaller or equal chain with us.')
			else:
				not_registered.append(address)
		except Exception as e:
			not_registered.append(address)
			print(e)
			continue
	return json.dumps({
		'registered': registered,
		'not_registered': not_registered
	})


# @app.route('/api/nodes/socialize', methods=['GET'])
# def send_registration_request():
# 	"""
# 	Pings every known peer to socialize with them, and register if
# 	not already.
# 	:return:
# 	"""
# 	peers = my_node.network.peers
# 	registered = []
# 	not_registered = []
# 	for peer in peers:
# 		try:
# 			data = [f'{request.host_url}:5000']
# 			headers = {'Content-Type': 'application/json'}
#
# 			response = requests.post(f'http://{peer}/api/nodes/register',
# 									 data=json.dumps(data), headers=headers)
#
# 			if response.status_code == 200:
# 				registered.append(str(peer))
# 			else:
# 				not_registered.append(str(peer))
# 		except Exception as e:
# 			not_registered.append(str(peer))
#
# 	return json.dumps({
# 		'registered': registered,
# 		'not_registered': not_registered
# 	})

# Testers
@app.route('/api/mine', methods=['GET'])
def try_mine():
	"""
	:return: Returns all pending transactions to be added to a block of a specific node.
	"""
	if not isinstance(my_node, Nodes.Miner):
		return json.dumps({
			'message': 'Node is not a miner -> Node can\'t mine!'
		}), 404
	mined = my_node.mine()
	if not mined:
		return json.dumps({
			'message': 'No transactions to mine!'
		})

	return json.dumps({
		'message': 'Block mined!'
	})
