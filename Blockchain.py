import json
import collections
import time
import binascii

from typing import List
from hashlib import sha256
from Client import Client


class Transaction:
	def __init__(self, sender: Client, recipient: str, value: float):
		self.sender = sender
		self.recipient = recipient
		self.value = value
		self.timestamp = time.time()
 
	def sign_transaction(self): 
		if not isinstance(self.sender, Client): 
			raise ValueError("Expected the sender to be a client!") 
 
		signer = self.sender.signer 
		h = sha256(json.dumps(self.__dict__, sort_keys=True).encode('utf-8'))
		return binascii.hexlify(signer.sign(h)).decode('ascii') 
 
	def print_transaction(self): 
		print("sender: \t", self.sender) 
		print("recipient: \t", self.recipient) 
		print("value: \t", str(self.value)) 
		print("time: \t", str(self.timestamp)) 

	def to_dict(self):
		return collections.OrderedDict({ 
			'sender': str(self.sender.identity), 
			'recipient': str(self.recipient), 
			'value': str(self.value), 
			'time': str(self.timestamp)})
	
	def toJSON(self):
		return json.dumps(self.to_dict())

	def __repr__(self):
		return self.toJSON()

	def __str__(self):
		return self.__str__()
	
class Block:

	def __init__(self, index: int, proof: int = 0, verified_transactions: List[Transaction] = [], previous_block_hash: str = None, timestamp=None):
		self.index: int = index
		self.proof: int = proof
		self.verified_transactions: List[Transaction] = verified_transactions
		self.previous_block_hash: str = previous_block_hash
		self.timestamp = time.time() # timestamp if timestamp else time.time

	@property	
	def calculate_hash(self) -> str:
		"""
		Returns the hash of the block by converting its instance into a JSON String.
		:return: Hash of the block
		"""
		return sha256(json.dumps(self.__dict__, sort_keys=True).encode('utf-8')).hexdigest()

	def to_dict(self):
		return collections.OrderedDict({ 
			'index': self.index,
			'proof': self.proof,
			'transactions': list(map(lambda o: o.to_dict(), self.verified_transactions)),
			'previous_hash':  self.previous_block_hash,
			'timestamp': self.timestamp})

	def toJSON(self):
		return json.dumps(self.to_dict())

	def __repr__(self):
		return self.toJSON()

	def __str__(self):
		return self.__str__()
	
class BlockChain:
	
	def __init__(self):
		self.chain: List[Block] = []
		self.unconfirmed_transactions: List[Transaction] = []
		self.nodes = set() 	# TODO: Create nodes network
		self.construct_genesis()
	
	def construct_genesis(self):
		self.construct_block(
			proof=42,
			previous_hash="Samira-mira-mira-e-e-Waka-Waka-e-e"
		)

	def construct_block(self, proof=None, previous_hash=None) -> Block:
		if proof is None or previous_hash is None:
			last_block = self.last_block
			proof = self.proof_of_work(last_block.proof)
			previous_hash = last_block.calculate_hash

		block = Block(
			index=len(self.chain),
			proof=proof,
			verified_transactions=self.unconfirmed_transactions,
			previous_block_hash=previous_hash)
		
		self.unconfirmed_transactions = []
		self.chain.append(block)
		return block

	def add_transaction(self, transaction: Transaction):
		# TODO: Validate Transaction?
		if not isinstance(transaction, Transaction):
			raise ValueError("Transaction is not a valid Transaction object!")

		return self.unconfirmed_transactions.append(transaction)

	def mine(self):
		if not self.unconfirmed_transactions:
			return False
		
		return self.construct_block()

	@staticmethod
	def check_validity(block: Block, prev_block: Block) -> bool:
		"""
		@return Wether the blockchain is valid or not
		"""
		if prev_block.index + 1 != block.index:
			return False
		elif prev_block.calculate_hash != block.previous_block_hash:
			return False
		elif len(block.verified_transactions) == 0 and block.index != 0:	# TODO: Ask about this one
			return False
		elif block.timestamp <= prev_block.timestamp:
			return False
		elif not BlockChain.verify_proof(block.proof, prev_block.proof):
			return False
		else:
			return True

	@staticmethod
	def verify_proof(prev_proof, proof, difficulty=2):
		if difficulty <= 0:
			raise ValueError("Difficulty must be a positive number!")

		guess = f'{prev_proof}{proof}'.encode()
		guess_hash = sha256(guess).hexdigest()
		return guess_hash[:difficulty] == "1"*difficulty

	@staticmethod
	def proof_of_work(last_proof) -> int:
		proof = 0
		while BlockChain.verify_proof(proof, last_proof) is False:
			proof += 1
		
		return proof

	@property
	def last_block(self) -> Block:
		return self.chain[-1]

	def dump_blockchain(self):
		print(f"Number of blocks in the chain: {len(self.chain)}")
		print("="*64)
		for x in range(len(self.chain)):
			block_temp = self.chain[x]
			print("block# " + str(x))
			for transaction in block_temp.verified_transactions:
				transaction.print_transaction()
				print('-'*16)
			print("="*64)

if __name__ == '__main__':
	clientA = Client()
	clientB = Client()

	blockchain = BlockChain()
	blockchain.dump_blockchain()

	t0 = Transaction(clientA, clientB, 5)
	t1 = Transaction(clientB, clientA, 2)

	blockchain.add_transaction(t0)
	blockchain.add_transaction(t1)
	blockchain.mine()

	print(blockchain.chain)