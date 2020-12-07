import binascii
import os
import uuid

import Crypto
from Crypto.PublicKey import RSA
from Crypto.PublicKey.RSA import RsaKey
from Crypto.Signature import pkcs1_15
from Crypto.Signature.pkcs1_15 import PKCS115_SigScheme

import UniCoin.helpers.paths as paths
import UniCoin.Blockchain as Blockchain
import UniCoin.Transactions as Transactions


class NodeNetwork:
	def __init__(self):
		self._nodes = set()

	def register_node(self, address: str):
		self._nodes.add(address)

	def blacklist_node(self, address: str):		# TODO: Is this possible for a blockchain network??
		pass


class Node:
	TYPE_CLIENT = 0,
	TYPE_MINER = 1

	def __init__(self, private_key: RsaKey):
		self.network: NodeNetwork = NodeNetwork()
		self.blockchain = Blockchain.BlockChain()
		self.private_key: RsaKey = private_key
		self.public_key: RsaKey = self.private_key.publickey()

	@property
	def identity(self) -> str:
		return binascii.hexlify(self.public_key.exportKey(format='DER')).decode('ascii')

	def __str__(self):
		return self.identity


class Client(Node):
	def __init__(self, private_key: RsaKey):
		super().__init__(private_key)
		self.signer: PKCS115_SigScheme = pkcs1_15.new(self.private_key)
		self.UTX = [] 	# List of unspent transactions

	def create_transaction(self):
		pass

	# def add_transaction(self, transaction) -> bool:
	# 	# if not isinstance(transaction, Transaction):
	# 	# 	raise ValueError("Transaction is not a valid Transaction object!")
	#
	# 	if transaction.check_validity():
	# 		self.transactions.append(transaction)  # TODO:
	# 		return True
	# 	print("ERROR -> INVALID TRANSACTION, ", transaction.check_validity())
	#
	# 	return False


class Miner(Client):
	def __init__(self, private_key: RsaKey):
		super().__init__(private_key)
		self.transactions = []
		# Unconventional, but i guess it's fine just for the demonstration
		# Miner shouldn't create Genesis block?
		self.construct_genesis()

	def construct_genesis(self):
		self.construct_block(
			proof=42,
			previous_hash="Samira-mira-mira-e-e-Waka-Waka-e-e"
		)

	def construct_block(self, verified_transactions=[], proof=None, previous_hash=None) -> Blockchain.Block:
		if proof is None or previous_hash is None:
			last_block = self.blockchain.last_block
			proof = Blockchain.proof_of_work(last_block.proof)
			previous_hash = last_block.calculate_hash

		block = Blockchain.Block(
			index=len(self.blockchain.chain),
			proof=proof,
			verified_transactions=verified_transactions,
			previous_block_hash=previous_hash)

		# TODO: Calculate fees too!
		# Coinbase Transaction
		coinbase = Transactions.Transaction(
			outputs=[Transactions.TransactionOutput(self.identity, block.reward + sum(list(map(lambda o: o.calculate_transaction_fee(self.blockchain.chain), verified_transactions))))]  # TODO: + fees
		)
		coinbase.sign_transaction(self)
		verified_transactions.insert(0, coinbase)

		# TODO: Broadcast BLOCK!
		self.blockchain.chain.append(block)
		return block

	def mine(self):
		if not self.transactions:
			return False

		return self.construct_block(
			verified_transactions=self.transactions,
		)

	def add_transaction(self, transaction) -> bool:
		# if not isinstance(transaction, Transactions.Transaction):
		# 	raise ValueError("Transaction is not a valid Transaction object!")

		if transaction.check_validity(self.blockchain.chain):
			self.transactions.append(transaction)  # TODO:
			return True
		print("ERROR -> INVALID TRANSACTION, ", transaction.check_validity(self.blockchain.chain))

		return False


class KeyFactory:
	"""
	Manages creating, storing or loading UniCoin Clients.
	"""

	@staticmethod
	def create_key() -> RsaKey:
		random = Crypto.Random.new().read
		return RSA.generate(1024, random)

	@staticmethod
	def store_key(key: RsaKey, friendly_name: str = None):
		if not isinstance(key, RsaKey):
			raise ValueError('First argument must be an RsaKey!')

		name = friendly_name if friendly_name else str(uuid.uuid4())
		file_name = f'{paths.PATH_WALLETS}/{name}.der'
		os.makedirs(os.path.dirname(file_name), exist_ok=True)
		with open(file_name, 'wb+') as file:
			file.write(key.exportKey(format='DER'))

	@staticmethod
	def load_key(name: str) -> RsaKey:
		with open(f'{paths.PATH_WALLETS}/{name}.der', 'rb') as file:
			key = file.read()

		return RSA.import_key(key)
