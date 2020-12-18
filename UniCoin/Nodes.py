import binascii
import json
import os
import uuid
import operator
import Crypto
import requests

from typing import List, Set
from Crypto.PublicKey import RSA
from Crypto.PublicKey.RSA import RsaKey
from Crypto.Signature import pkcs1_15
from Crypto.Signature.pkcs1_15 import PKCS115_SigScheme

import UniCoin.helpers.paths as paths
import UniCoin.Blockchain as Blockchain
import UniCoin.Transactions as Transactions


class Peer:
	def __init__(self, address: str, port: int):
		"""
		Peer entity.
		Each peer is basically a node that we can send/receive information.
		:param address: IP Address of the peer
		:param port: Port of the peer
		"""
		self.address: str = address
		self.port: int = port

	def __str__(self):
		return f'{self.address}:{self.port}'

	def __hash__(self):
		return hash((self.address, self.port))

	def __eq__(self, other):
		if not isinstance(other, Peer):
			return NotImplemented

		return self.address == other.address and self.port == other.port


class PeerNetwork:
	"""
	Network of peers stored in each node.
	Handles registration/incoming messages etc.
	"""
	def __init__(self):
		self._peers = set()

	def register_peer(self, peer: Peer):
		if peer in self._peers:
			return False

		self._peers.add(peer)
		return True

	@staticmethod
	def check_chain_length(peer: Peer) -> int:
		"""
		:param peer:
		:return: Length of peer's blockchain.
		"""
		response = requests.get(f'http://{peer}/api/blockchain/length')

		if response.status_code == 200:
			try:
				json_data = json.loads(response.text)
				length = json_data["length"]
				return json_data["length"]
			except Exception:
				print(f'Failed fetching blockchain length from peer {peer}')
				return 0
		return 0

	@staticmethod
	def steal_chain(peer: Peer) -> Blockchain.BlockChain:
		"""
		Grab the chain, validate it and if everything is good, swap it with ours.
		:param peer:
		:return:
		"""
		response = requests.get(f'http://{peer}/api/blockchain/chain')

		if response.status_code == 200:
			try:
				json_data = json.loads(response.text)
				chain_data = json_data["chain"]
				return Blockchain.BlockChain
			except Exception:
				print(f'Failed fetching blockchain from peer {peer}')
				return None
		return None

	def blacklist_peer(self, address: str):  # TODO: Is this possible for a blockchain network??
		pass

	@property
	def peers(self):
		return self._peers


class Node:
	TYPE_CLIENT = 0,
	TYPE_MINER = 1

	def __init__(self, private_key: RsaKey):
		self.network: PeerNetwork = PeerNetwork()
		self.blockchain = Blockchain.BlockChain()
		self.private_key: RsaKey = private_key
		self.public_key: RsaKey = self.private_key.publickey()

	@property
	def identity(self) -> str:
		return binascii.hexlify(self.public_key.exportKey(format='DER')).decode('ascii')

	@property
	def type(self):
		return self.TYPE_UNINITIALIZED

	def __str__(self):
		return self.identity


class Client(Node):
	def __init__(self, private_key: RsaKey):
		super().__init__(private_key)
		self.signer: PKCS115_SigScheme = pkcs1_15.new(self.private_key)
		self.UTXOs: Set[Transactions.TransactionInput] = set()  # List of unspent transactions

	def send_coins(self, transactions: tuple) -> bool:
		transaction_outputs: List[Transactions.TransactionOutput] = []
		total_balance = 0
		allocated_balance = 0
		# Create Transaction Outputs
		for t in transactions:
			try:
				if isinstance(t[0], str) and isinstance(t[1], int) and t[1] > 0:
					transaction_outputs.append(
						Transactions.TransactionOutput(
							recipient_address=t[0],
							value=t[1]
						)
					)
					total_balance += t[1]
			except Exception:
				print('Failed parsing transactions. Wrong tuple provided.')
				return False

		# Allocate enough funds
		sorted_utxo: List[Transactions.TransactionInput] = sorted(self.UTXOs, key=operator.attrgetter('balance'))
		selected_utxo: List[Transactions.TransactionInput] = []
		for utxo in sorted_utxo:
			if allocated_balance >= total_balance:
				break

			if utxo.balance == -1:
				continue

			selected_utxo.append(utxo)
			allocated_balance += utxo.balance

		# Verify we have enough funds
		if total_balance > allocated_balance:
			return False

		transaction = Transactions.Transaction(
			sender=self.identity,
			inputs=tuple(selected_utxo),
			outputs=tuple(transaction_outputs),
		)
		transaction.sign_transaction(self)

		# TODO: Broadcast Transaction
		return transaction  # TODO: Remove tester
		return True


class Miner(Client):
	def __init__(self, private_key: RsaKey):
		super().__init__(private_key)
		self.verified_transactions: List = []  # Store Verified transactions to input in block

		# Unconventional, but i guess it's fine just for the demonstration
		# Miner shouldn't create Genesis block?
		self.__construct_genesis()

	def __construct_genesis(self):
		self.construct_block(
			proof=42,
			previous_hash="Samira-mira-mira-e-e-Waka-Waka-e-e"
		)

	def construct_block(self, verified_transactions: List[Transactions.Transaction] = [],
						proof=None, previous_hash=None) -> Blockchain.Block:
		if proof is None or previous_hash is None:
			last_block = self.blockchain.last_block
			proof = Blockchain.proof_of_work(last_block.proof)
			previous_hash = last_block.calculate_hash()

		block = Blockchain.Block(
			index=len(self.blockchain.blocks),
			proof=proof,
			verified_transactions=verified_transactions,
			previous_block_hash=previous_hash)

		coinbase_total = block.reward + sum([trans.transaction_fee for trans in verified_transactions])

		# Coinbase Transaction
		coinbase = Transactions.Transaction(
			outputs=[
				Transactions.TransactionOutput(
					self.identity,
					coinbase_total
				)
			]
		)
		coinbase.sign_transaction(self)
		verified_transactions.insert(0, coinbase)

		# TODO: Broadcast BLOCK!
		self.blockchain.blocks.append(block)
		self.UTXOs.add(
			Transactions.TransactionInput(
				block.index, 0, 0, coinbase_total
			)
		)
		return block

	def mine(self):
		"""
		Mine --WITHOUT TRANSACTION LIMIT--
		:return:
		"""
		if not self.verified_transactions:
			return False

		#TODO: Broadcast block
		new_block = self.construct_block(
			verified_transactions=self.verified_transactions,
		)
		print(new_block)
		return new_block

	def add_transaction(self, transaction) -> bool:
		if not isinstance(transaction, Transactions.Transaction):
			raise ValueError("Transaction is not a valid Transaction object!")

		if transaction.check_validity(self.blockchain.blocks):
			self.verified_transactions.append(transaction)
			return True

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
