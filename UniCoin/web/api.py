import json
import UniCoin.Nodes as Nodes
import UniCoin.Transactions as Transactions
import UniCoin.Blockchain as Blockchain

from flask import request
from UniCoin import app, my_node

import logging
log = logging.getLogger('werkzeug')

# TODO: Maybe routes should only be used to verify inputs
# TODO: Then proceed in Controller classes?


# --- BROADCAST ROUTES ---
@app.route('/api/broadcasts/new_block', methods=['POST'])
def broadcasts_new_block():
	"""
	:return:
	"""
	json_data = request.get_json()
	if not json_data:
		return json.dumps({
			'message': 'Incorrect JSON Data.'
		}), 400
	data = json.loads(json_data)
	block = Blockchain.Block.from_json(data)

	log.debug(f'[BLOCK] Received:  \'{block.hash}\'')
	if isinstance(my_node, Nodes.Miner):
		if block.check_validity(my_node.blockchain.last_block):
			log.debug(f'[BLOCK] Validated: \'{block.hash}\'')
			my_node.blockchain.blocks.append(block)

			# -- UPDATE UTXO SET --
			my_node.UTXOs.difference_update(block.extract_STXOs())
			my_node.UTXOs = my_node.UTXOs.union(block.extract_UTXOs())
			# ---------------------

			my_node.network.broadcast_block(block)
		else:
			if block.index > my_node.blockchain.last_block.index + 1:
				log.debug(f'[BLOCK] Rejected (AHEAD): \'{block.hash}\'')
				chain = my_node.network.check_peer_chains(my_node.blockchain.size)
				if chain:
					log.debug('[BLOCKCHAIN] Fetched bigger valid chain.')
					# TODO: Must update UTXOs!
					my_node.blockchain = chain
			else:
				log.debug(f'[BLOCK] Rejected (INVALID): \'{block.hash}\'')
	elif type(my_node) is Nodes.Client:
		log.debug(f'[BLOCK] ECHOING: \'{block.hash}\'')
		# TODO: Check if is_valid (lite edition)?
		if block.check_validity(my_node.blockchain.last_block, lite=True):
			my_node.network.broadcast_block(block)  # Echo Transaction

	return json.dumps({
		'message': 'ok',
	})


@app.route('/api/broadcasts/new_transaction', methods=['POST'])
def broadcasts_new_transaction():
	"""
	:return:
	"""
	json_data = request.get_json()
	if not json_data:
		return json.dumps({
			'message': 'Incorrect JSON Data.'
		}), 400
	data = json.loads(json_data)
	transaction = Transactions.Transaction.from_json(data)
	if isinstance(my_node, Nodes.Miner):
		success = my_node.add_transaction(transaction)
		if success:
			log.debug(f'[TRANSACTION] Validated: \'{transaction.hash}\'')
			my_node.network.broadcast_transaction(transaction)
		else:
			log.debug(f'[TRANSACTION] Rejected (INVALID or EXISTS): \'{transaction.hash}\'')
	elif isinstance(my_node, Nodes.Client):
		log.debug(f'[TRANSACTION] ECHOING: \'{transaction.hash}\'')
		my_node.network.broadcast_transaction(transaction)

	return json.dumps({
		'message': 'ok',
	})


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
	"""
	if not isinstance(my_node, (Nodes.Miner, Nodes.Client)):
		return json.dumps({
			'message': 'Node must be a client or miner to have UTXO.'
		}), 404

	# TODO: Create transaction!
	return json.dumps({
		'length': len(my_node.my_UTXOs),
		'total': sum([t.value for t in my_node.my_UTXOs]),
		'UTXOs':  list(map(lambda o: o.to_dict(), my_node.my_UTXOs)),
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
		'node_type': str(type(my_node).__name__).upper(),
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
					log.debug(f'[PEER] \'{peer}\' has longer blockchain length.')
					chain = my_node.network.steal_chain(peer)
					if chain.check_validity():
						my_node.blockchain = chain
						log.debug(f'[PEER] Now using the blockchain of peer \'{peer}\'')
					else:
						log.debug(f'[PEER] Failed to validate blockchain of peer \'{peer}\'.')
			else:
				not_registered.append(address)
		except Exception as e:
			not_registered.append(address)
			log.error(e)
			continue
	return json.dumps({
		'registered': registered,
		'not_registered': not_registered
	})
