import json
import collections
import time

from typing import List
from Crypto.Hash import SHA256

import UniCoin.Transactions as Transactions


def verify_proof(prev_proof, proof, difficulty=2) -> bool:
	if difficulty <= 0:
		raise ValueError("Difficulty must be a positive number!")

	guess = f'{prev_proof}{proof}'.encode()
	guess_hash = SHA256.new(guess).hexdigest()
	return guess_hash[:difficulty] == "1" * difficulty


def proof_of_work(last_proof: int) -> int:
	proof = 0
	while verify_proof(proof, last_proof) is False:
		proof += 1

	return proof


class Block:
	def __init__(self, index: int, proof: int = 0, verified_transactions: list = [], previous_block_hash: str = None):
		self.index: int = index
		self.proof: int = proof
		self.verified_transactions: List[Transactions.Transaction] = verified_transactions
		self.previous_block_hash: str = previous_block_hash
		self.timestamp = time.time()

	def check_validity(self, prev_block) -> bool:
		"""
		:return: Whether the block is valid or not
		"""
		if not isinstance(prev_block, Block):
			return False
		elif prev_block.index + 1 != self.index:
			return False
		elif prev_block.calculate_hash != self.previous_block_hash:
			return False
		elif len(self.verified_transactions) == 0 and self.index != 0:  # TODO: Ask about this one
			return False
		elif self.timestamp <= prev_block.timestamp:
			return False
		elif not self.verify_proof(self.proof, prev_block.proof):
			return False
		else:
			return True

	@property
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

	def to_dict(self):
		return collections.OrderedDict({
			'index': self.index,
			'proof': self.proof,
			'transactions': list(map(lambda o: o.to_dict(), self.verified_transactions)),
			'previous_hash': self.previous_block_hash,
			'timestamp': self.timestamp})

	def to_json(self):
		return json.dumps(self.to_dict(), sort_keys=True).encode('utf-8')

	def __repr__(self):
		return self.to_json()

	def __str__(self):
		return self.__str__()


class BlockChain:

	def __init__(self):
		self.chain: List[Block] = []
		self.transactions: list = []

	@property
	def last_block(self) -> Block:
		return self.chain[-1]

	@property
	def size(self) -> int:
		return len(self.chain)

	def check_validity(self) -> bool:
		"""
		:return: Whether the Blockchain is valid or not.
		"""
		block = self.last_block
		while block.index >= 1:
			prev_block = self.chain[block.index - 1]
			if not block.check_validity(prev_block):
				return False

		return True

	def dump_blockchain(self):
		print('=' * 23, f'[BLOCKCHAIN - {len(self.chain)}]', '=' * 23)
		print("TODO - INFO ABOUT THE BLOCKCHAIN?")  # TODO: Info about the blockchain?
		print('=' * 64)
		for x in range(len(self.chain)):
			block = self.chain[x]
			print(f'block#{x} \t | TX - {len(block.verified_transactions)}\t |')
			print('-' * 64)
			for transaction in block.verified_transactions:
				transaction.print_transaction()
				print('-' * 64)
			print("=" * 64)


if __name__ == '__main__':
	pass
	# clientA = Client()
	# clientB = Client()
	#
	# blockchain = BlockChain()
	# blockchain.dump_blockchain()
	#
	# t0 = Transaction(clientA.identity, clientB.identity, 5)
	# t0.print_transaction()
	# block = blockchain.construct_block(verified_transactions=[t0])
	# print(block.to_json())
	# blockchain.dump_blockchain()
	# t0.sign_transaction(clientA)
	# t0.print_transaction()
	#
	# ------ Invalidate Transaction for Fun ------
	# print(f'Transaction is valid?: {t0.verify_transaction()}')
	# print(t0.sender)
	# t0.sender = binascii.hexlify(RSA.generate(1024, Crypto.Random.new().read).publickey().exportKey(format='DER')).decode('ascii')
	# print(t0.sender)
	# print(f'Transaction is valid?: {t0.verify_transaction()}')
	#
	# t1 = Transaction(clientB, clientA, 2)
	#
	# blockchain.add_transaction(t0)
	# blockchain.add_transaction(t1)
	# blockchain.mine()
	#
	# print(blockchain.chain)