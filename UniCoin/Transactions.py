import json
import collections
import time
import binascii
import UniCoin.Nodes
import UniCoin.Blockchain

from typing import List
from Crypto.Hash import SHA256
from Crypto.PublicKey import RSA
from Crypto.Signature import pkcs1_15

from UniCoin.decorators import singleton


class TransactionInput:		# Simplified UTXO
	def __init__(self, block_index: int, transaction_index: int, output_index: int, balance: int = 0):
		self.block_index: int = block_index
		self.transaction_index: int = transaction_index
		self.output_index: int = output_index
		self.balance: int = 0							# Not actual balance, just the one stored if Transaction Input belongs to client

	def calculate_balance(self):
		"""
		:return:
		"""
		try:
			block: Block = BlockChain. .chain[self.block_index]
			return 0
		except Exception:
			return -1

	def to_dict(self):
		return collections.OrderedDict({
			'block_index': self.block_index,
			'transaction_index': self.transaction_index,
			'output_index': self.output_index})


class TransactionOutput:
	def __init__(self, recipient_address: str, value: int):
		self.recipient_address: str = None
		self.value: int = None

	def check_validity(self) -> bool:
		return self.value > 0

	def to_dict(self):
		return collections.OrderedDict({
			'recipient_address': self.recipient_address,
			'value': self.value
		})


class ATransaction:
	def __init__(self, sender: str, inputs: List[TransactionInput], outputs: List[TransactionOutput]):
		self.sender = sender  # Better alternative -> Sender could be found dynamically by getting first transaction output?
		self.inputs: List[TransactionInput] = inputs
		self.outputs: List[TransactionOutput] = outputs
		self.timestamp = time.time()
		self.signature = None

	@property
	def balance_input(self) -> int:
		return sum([inp.balance for inp in self.inputs])

	@property
	def balance_output(self) -> int:
		return sum([out.value for out in self.outputs])

	@property
	def transaction_fee(self) -> int:
		return self.balance_output - self.balance_input

	def sign_transaction(self, sender: Client):
		if not isinstance(sender, Client):
			raise ValueError("Expected the sender to be a client!")

		signer = sender.signer

		self.signature = None
		h = SHA256.new(self.to_json())
		self.signature = binascii.hexlify(signer.sign(h)).decode('ascii')

	def verify_signature(self) -> bool:
		"""
		:return: Whether the signature belongs to the actual sender or not
		"""
		try:
			signature = self.signature
			self.signature = None						# Remove signature to verify hash

			der_key = binascii.unhexlify(self.sender)
			sig = binascii.unhexlify(signature)

			public_key = RSA.import_key(der_key)
			h = SHA256.new(self.to_json())

			signer = pkcs1_15.new(public_key)
			signer.verify(h, sig)						# Verify that the hash and transaction match
			result = True
		except (ValueError, TypeError, Exception):
			result = False
		finally:
			self.signature = signature					# Reset signature
			return result

	def check_validity(self) -> bool:
		if not self.verify_signature():
			return False

		if not self.transaction_fee >= 0:				# Output is more than available input
			return False

		return True						 				# TODO: Check previous blocks!

	def print_transaction(self):
		print("sender: \t", self.sender)
		print("recipient: \t", self.recipient)
		print("value: \t", str(self.value))
		print("time: \t", str(self.timestamp))
		print("signature: \t", str(self.signature))

	def to_dict(self):
		return collections.OrderedDict({
			'inputs': self.inputs,
			'outputs': self.outputs,
			'timestamp': self.timestamp,
			'signature': self.signature,
		})

	def to_json(self):
		return json.dumps(self.to_dict(), sort_keys=True).encode('utf-8')

	def __repr__(self):
		return self.toJSON()

	def __str__(self):
		return self.__str__()


class Transaction:
	def __init__(self, sender_addr: str, recipient_addr: str, value: float):
		self.sender = sender_addr
		self.recipient = recipient_addr
		self.value = value
		self.timestamp = time.time()
		self.signature = None

	def sign_transaction(self, sender: Client):
		if not isinstance(sender, Client):
			raise ValueError("Expected the sender to be a client!")

		signer = sender.signer

		self.signature = None
		h = SHA256.new(self.to_json())
		self.signature = binascii.hexlify(signer.sign(h)).decode('ascii')

	def verify_signature(self) -> bool:
		try:
			signature = self.signature
			self.signature = None						# Remove signature to verify hash

			der_key = binascii.unhexlify(self.sender)
			sig = binascii.unhexlify(signature)

			public_key = RSA.import_key(der_key)
			h = SHA256.new(self.to_json())

			signer = pkcs1_15.new(public_key)
			signer.verify(h, sig)						# Verify that the hash and transaction match
			result = True
		except (ValueError, TypeError, Exception):
			result = False
		finally:
			self.signature = signature					# Reset signature
			return result

	def check_validity(self) -> bool:
		return self.verify_signature()

	def print_transaction(self):
		print("sender: \t", self.sender)
		print("recipient: \t", self.recipient)
		print("value: \t", str(self.value))
		print("time: \t", str(self.timestamp))
		print("signature: \t", str(self.signature))

	def to_dict(self):
		return collections.OrderedDict({
			'sender': self.sender,
			'recipient': self.recipient,
			'value': self.value,
			'time': self.timestamp,
			'signature': self.signature})

	def to_json(self):
		return json.dumps(self.to_dict(), sort_keys=True).encode('utf-8')

	def __repr__(self):
		return self.toJSON()

	def __str__(self):
		return self.__str__()


@singleton
class TransactionManager:
	def __init__(self):
		self.unverified_transactions = []
		self.verified_transactions = []

	def add_transaction(self, transaction: Transaction) -> bool:
		if not isinstance(transaction, Transaction):
			raise ValueError("Transaction is not a valid Transaction object!")

		if transaction.check_validity():
			self.transactions.append(transaction)
			return True

		return False

	def broadcast_transaction(self): 	# TODO: Broadcast Transaction
		pass

	def clean_transactions(self):
		pass


if __name__ == '__main__':

	from UniCoin.Nodes import KeyFactory, Miner
	from UniCoin.Blockchain import BlockChain, Block

	print('--- Transaction check ---')
	clientA = Client(KeyFactory.create_key())
	clientB = Client(KeyFactory.create_key())
	minerA = Miner(KeyFactory.create_key())

	BlockChain().dump_blockchain()
	minerA.mine()
	BlockChain().dump_blockchain()

	# in0 = TransactionInput()
	# t0 = ATransaction(clientA.identity, [], [])
	# t0.sign_transaction(clientA)
	#
	# print(t0.__dict__)
