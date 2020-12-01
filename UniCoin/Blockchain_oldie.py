# import json
# import collections
# import time
# import binascii
#
# from typing import List
# from Crypto.Hash import SHA256
# from Crypto.PublicKey import RSA
# from Crypto.Signature import pkcs1_15
#
# from UniCoin.Client import Client
#
#
# class Transaction:
# 	def __init__(self, sender_addr: str, recipient_addr: str, value: float):
# 		self.sender = sender_addr
# 		self.recipient = recipient_addr
# 		self.value = value
# 		self.timestamp = time.time()
# 		self.signature = None
#
# 	def sign_transaction(self, sender: Client):
# 		if not isinstance(sender, Client):
# 			raise ValueError("Expected the sender to be a client!")
#
# 		signer = sender.signer
#
# 		self.signature = None
# 		h = SHA256.new(self.to_json())
# 		self.signature = binascii.hexlify(signer.sign(h)).decode('ascii')
#
# 	def verify_signature(self) -> bool:
# 		try:
# 			signature = self.signature
# 			self.signature = None						# Remove signature to verify hash
#
# 			der_key = binascii.unhexlify(self.sender)
# 			sig = binascii.unhexlify(signature)
#
# 			public_key = RSA.import_key(der_key)
# 			h = SHA256.new(self.to_json())
#
# 			signer = pkcs1_15.new(public_key)
# 			signer.verify(h, sig)						# Verify that the hash and transaction match
# 			result = True
# 		except (ValueError, TypeError, Exception):
# 			result = False
# 		finally:
# 			self.signature = signature					# Reset signature
# 			return result
#
# 	def check_validity(self) -> bool:
# 		return self.verify_signature()
#
# 	def print_transaction(self):
# 		print("sender: \t", self.sender)
# 		print("recipient: \t", self.recipient)
# 		print("value: \t", str(self.value))
# 		print("time: \t", str(self.timestamp))
# 		print("signature: \t", str(self.signature))
#
# 	def to_dict(self):
# 		return collections.OrderedDict({
# 			'sender': self.sender,
# 			'recipient': self.recipient,
# 			'value': self.value,
# 			'time': self.timestamp,
# 			'signature': self.signature})
#
# 	def to_json(self):
# 		return json.dumps(self.to_dict(), sort_keys=True).encode('utf-8')
#
# 	def __repr__(self):
# 		return self.toJSON()
#
# 	def __str__(self):
# 		return self.__str__()
#
#
# class Block:
# 	def __init__(self, index: int, proof: int = 0, verified_transactions: List[Transaction] = [],
# 				 previous_block_hash: str = None, timestamp=None):
# 		self.index: int = index
# 		self.proof: int = proof
# 		self.verified_transactions: List[Transaction] = verified_transactions
# 		self.previous_block_hash: str = previous_block_hash
# 		self.timestamp = time.time()  # timestamp if timestamp else time.time
#
# 	def check_validity(self, prev_block) -> bool:
# 		"""
# 		:return: Whether the block is valid or not
# 		"""
# 		if not isinstance(prev_block, Block):
# 			return False
# 		elif prev_block.index + 1 != self.index:
# 			return False
# 		elif prev_block.calculate_hash != self.previous_block_hash:
# 			return False
# 		elif len(self.verified_transactions) == 0 and self.index != 0:  # TODO: Ask about this one
# 			return False
# 		elif self.timestamp <= prev_block.timestamp:
# 			return False
# 		elif not self.verify_proof(self.proof, prev_block.proof):
# 			return False
# 		else:
# 			return True
#
# 	@staticmethod
# 	def verify_proof(prev_proof, proof, difficulty=2) -> bool:
# 		if difficulty <= 0:
# 			raise ValueError("Difficulty must be a positive number!")
#
# 		guess = f'{prev_proof}{proof}'.encode()
# 		guess_hash = SHA256.new(guess).hexdigest()
# 		return guess_hash[:difficulty] == "1" * difficulty
#
# 	@property
# 	def calculate_hash(self) -> str:
# 		"""
# 		Returns the hash of the block by converting its instance into a JSON String.
# 		:return: Hash of the block
# 		"""
# 		return SHA256.new(self.to_json()).hexdigest()
#
# 	def to_dict(self):
# 		return collections.OrderedDict({
# 			'index': self.index,
# 			'proof': self.proof,
# 			'transactions': list(map(lambda o: o.to_dict(), self.verified_transactions)),
# 			'previous_hash': self.previous_block_hash,
# 			'timestamp': self.timestamp})
#
# 	def to_json(self):
# 		return json.dumps(self.to_dict(), sort_keys=True).encode('utf-8')
#
# 	def __repr__(self):
# 		return self.to_json()
#
# 	def __str__(self):
# 		return self.__str__()
#
#
# class BlockChain2:
# 	def __init__(self):
# 		self.chain: List[Block] = []
#
# 	@staticmethod
# 	def proof_of_work(last_proof) -> int:
# 		proof = 0
# 		while BlockChain.verify_proof(proof, last_proof) is False:
# 			proof += 1
#
# 		return proof
#
# 	@property
# 	def last_block(self) -> Block:
# 		return self.chain[-1]
#
#
# class BlockChain:
# 	def __init__(self):
# 		self.chain: List[Block] = []
# 		self.unconfirmed_transactions: List[Transaction] = []
# 		self.construct_genesis()
#
# 	def construct_genesis(self):
# 		self.construct_block(
# 			proof=42,
# 			previous_hash="Samira-mira-mira-e-e-Waka-Waka-e-e"
# 		)
#
# 	def construct_block(self, proof=None, previous_hash=None) -> Block:
# 		if proof is None or previous_hash is None:
# 			last_block = self.last_block
# 			proof = self.proof_of_work(last_block.proof)
# 			previous_hash = last_block.calculate_hash
#
# 		block = Block(
# 			index=len(self.chain),
# 			proof=proof,
# 			verified_transactions=self.unconfirmed_transactions,
# 			previous_block_hash=previous_hash)
#
# 		self.unconfirmed_transactions = []
# 		self.chain.append(block)
# 		return block
#
# 	def add_transaction(self, transaction: Transaction) -> bool:
# 		if not isinstance(transaction, Transaction):
# 			raise ValueError("Transaction is not a valid Transaction object!")
#
# 		if transaction.check_validity():
# 			self.unconfirmed_transactions.append(transaction)
# 			return True
#
# 		return False
#
# 	def mine(self):
# 		if not self.unconfirmed_transactions:
# 			return False
#
# 		return self.construct_block()
#
# 	@staticmethod
# 	def check_validity(block: Block, prev_block: Block) -> bool:
# 		"""
# 		@return Whether the blockchain is valid or not
# 		"""
# 		if prev_block.index + 1 != block.index:
# 			return False
# 		elif prev_block.calculate_hash != block.previous_block_hash:
# 			return False
# 		elif len(block.verified_transactions) == 0 and block.index != 0:  # TODO: Ask about this one
# 			return False
# 		elif block.timestamp <= prev_block.timestamp:
# 			return False
# 		elif not BlockChain.verify_proof(block.proof, prev_block.proof):
# 			return False
# 		else:
# 			return True
#
# 	@staticmethod
# 	def verify_proof(prev_proof, proof, difficulty=2):
# 		if difficulty <= 0:
# 			raise ValueError("Difficulty must be a positive number!")
#
# 		guess = f'{prev_proof}{proof}'.encode()
# 		guess_hash = SHA256.new(guess).hexdigest()
# 		return guess_hash[:difficulty] == "1" * difficulty
#
# 	@staticmethod
# 	def proof_of_work(last_proof) -> int:
# 		proof = 0
# 		while BlockChain.verify_proof(proof, last_proof) is False:
# 			proof += 1
#
# 		return proof
#
# 	@property
# 	def last_block(self) -> Block:
# 		return self.chain[-1]
#
# 	def dump_blockchain(self):
# 		print(f"Number of blocks in the chain: {len(self.chain)}")
# 		print("=" * 64)
# 		for x in range(len(self.chain)):
# 			block_temp = self.chain[x]
# 			print("block# " + str(x))
# 			for transaction in block_temp.verified_transactions:
# 				transaction.print_transaction()
# 				print('-' * 16)
# 			print("=" * 64)
#
#
# if __name__ == '__main__':
# 	clientA = Client()
# 	clientB = Client()
#
# 	blockchain = BlockChain()
# 	blockchain.dump_blockchain()
#
# 	t0 = Transaction(clientA.identity, clientB.identity, 5)
# 	t0.print_transaction()
# 	t0.sign_transaction(clientA)
# 	t0.print_transaction()
#
# 	# ------ Invalidate Transaction for Fun ------
# 	# print(f'Transaction is valid?: {t0.verify_transaction()}')
# 	# print(t0.sender)
# 	# t0.sender = binascii.hexlify(RSA.generate(1024, Crypto.Random.new().read).publickey().exportKey(format='DER')).decode('ascii')
# 	# print(t0.sender)
# 	# print(f'Transaction is valid?: {t0.verify_transaction()}')
#
# 	# t1 = Transaction(clientB, clientA, 2)
# 	#
# 	# blockchain.add_transaction(t0)
# 	# blockchain.add_transaction(t1)
# 	# blockchain.mine()
# 	#
# 	# print(blockchain.chain)
