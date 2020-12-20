import hashlib
import json
import collections
import time

import UniCoin.Transactions as Transactions

from typing import List
from Crypto.Hash import SHA256


def verify_proof(prev_proof, proof, difficulty=2) -> bool:
	"""
	Verifying if the Proof-of-Work is correct, based on a specific difficulty.
	:param prev_proof: Proof-of-Work of previous block.
	:param proof: Proof-of-Work that is to be checked.
	:param difficulty: Difficulty level that is to be checked.
	:return: Whether the Proof-of-Work found is valid or not.
	"""
	if difficulty <= 0:
		raise ValueError("Difficulty must be a positive number!")

	guess = f'{prev_proof}{proof}'.encode()
	guess_hash = SHA256.new(guess).hexdigest()
	return guess_hash[:difficulty] == "1" * difficulty


def proof_of_work(prev_proof: int, difficulty=2) -> int:
	"""
	Proof-of-Work algorithm. Increment a random number and trying to verify it
	each time until Proof-of-work returns True.
	:param prev_proof: Proof-of-Work of previous block.
	:param difficulty: Difficulty level of mining.
	:return:
	"""
	proof = 0
	while verify_proof(prev_proof, proof, difficulty) is False:
		proof += 1

	return proof


class Block:
	"""
	Block Instance
	------------------
	A single block of the blockchain, containing the proof-of-work of the previous block alongside with the
	verified transactions.
	"""
	def __init__(self, index: int, proof: int = 0, verified_transactions: list = [], previous_block_hash: str = None,
				 timestamp: float = None):
		self.index: int = index
		self.proof: int = proof
		self.verified_transactions: List[Transactions.Transaction] = verified_transactions
		self.previous_block_hash: str = previous_block_hash
		self.timestamp = timestamp or time.time()

	def check_validity(self, prev_block) -> bool:
		"""
		:return: Whether the block is valid or not
		"""
		print(f'checking block validity {self.index}')
		if not isinstance(prev_block, Block):
			return False
		elif prev_block.index + 1 != self.index:
			print('incr')
			return False
		elif prev_block.calculate_hash() != self.previous_block_hash:
			print('hash')
			return False
		elif len(self.verified_transactions) == 0 and self.index != 0:  # TODO: Ask about this one
			print('trans')
			return False
		elif self.timestamp <= prev_block.timestamp:
			print(f'timestamp {self.timestamp} <= {prev_block.timestamp}')
			return False
		elif not verify_proof(prev_block.proof, self.proof):
			print('proof')
			return False
		else:
			return True

	def calculate_hash(self) -> str:
		"""
		Returns the hash of the block by converting its instance into a JSON String.
		:return: Hash of the block
		"""
		return SHA256.new(self.to_json()).hexdigest()

	@property
	def reward(self) -> int:
		"""
		Reduce block reward by 5 per 4 mining operations.
		Total coins in circulation should be 1050
		:return:
		"""
		return max([0, 50 - 5 * ((self.index + 1) // 4)])  # TODO: Maybe create an actual reward algorithm?

	@property
	def hash(self) -> str:
		return hashlib.md5(self.to_json()).hexdigest()

	def to_dict(self):
		return collections.OrderedDict({
			'index': self.index,
			'proof': self.proof,
			'transactions': list(map(lambda o: o.to_dict(), self.verified_transactions)),
			'previous_hash': self.previous_block_hash,
			'timestamp': self.timestamp})

	def to_json(self, indent=None):
		return json.dumps(self.to_dict(), sort_keys=True, indent=indent).encode('utf-8')

	@classmethod
	def from_json(cls, data):
		index = int(data['index'])
		proof = int(data['proof'])
		verified_transactions = list(map(Transactions.Transaction.from_json, data['transactions']))
		previous_block_hash = str(data['previous_hash'])
		timestamp = float(data['timestamp'])

		return cls(
			index=index,
			proof=proof,
			verified_transactions=verified_transactions,
			previous_block_hash=previous_block_hash,
			timestamp=timestamp
		)

	def __repr__(self):
		return self.to_json()

	def __str__(self):
		return str(self.to_json(indent=4).decode('utf-8'))


class BlockChain:
	"""
	BlockChain
	------------------
	The BlockChain. ¯\_(ツ)_/¯
	"""
	def __init__(self, blocks: List[Block] = []):
		self.blocks: List[Block] = blocks
		self.transactions: list = []

	@property
	def last_block(self) -> Block:
		return self.blocks[-1]

	@property
	def size(self) -> int:
		return len(self.blocks)

	def check_validity(self) -> bool:
		"""
		:return: Whether the Blockchain is valid or not.
		"""
		block = self.last_block
		while block.index >= 1:
			prev_block = self.blocks[block.index - 1]
			if not block.check_validity(prev_block):
				return False
			block = prev_block

		return True

	def to_dict(self):
		return collections.OrderedDict({
			'length': self.size,
			'chain': tuple(map(lambda o: o.to_dict(), self.blocks)),
		})

	def to_json(self, indent=None):
		return json.dumps(self.to_dict(), sort_keys=True, indent=indent).encode('utf-8')

	@classmethod
	def from_json(cls, data):
		blocks = list(map(Block.from_json, data['chain']))

		return cls(
			blocks=blocks
		)

	def __repr__(self):
		return self.to_json()

	def __str__(self):
		return str(self.to_json(indent=4).decode('utf-8'))
