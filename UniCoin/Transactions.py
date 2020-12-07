import json
import collections
import time
import binascii

from typing import List
from Crypto.Hash import SHA256
from Crypto.PublicKey import RSA
from Crypto.Signature import pkcs1_15

import UniCoin.Nodes as Nodes
import UniCoin.Blockchain as Blockchain


class TransactionInput:		# Simplified UTXO
	def __init__(self, block_index: int, transaction_index: int, output_index: int):
		self.block_index: int = block_index
		self.transaction_index: int = transaction_index
		self.output_index: int = output_index

	def real_balance(self, chain: list):
		"""
		:return:
		"""
		try:
			block: Blockchain.Block = chain[self.block_index]

			# TODO: Change this when adding TRANSACTIONS
			transaction = block.verified_transactions[self.transaction_index]
			output = transaction.outputs[self.output_index]
			return output.value
		except Exception:
			print("EXCEPTION -1 BALANCE")
			return -1

	def check_validity(self, chain) -> bool:
		return self.real_balance(chain) > 0

	def to_dict(self):
		return collections.OrderedDict({
			'block_index': self.block_index,
			'transaction_index': self.transaction_index,
			'output_index': self.output_index})

	def to_json(self):
		return json.dumps(self.to_dict(), sort_keys=True).encode('utf-8')

	def __repr__(self):
		return self.to_json()

	def __str__(self):
		return self.__repr__()


class TransactionOutput:
	def __init__(self, recipient_address: str, value: int):
		self.recipient_address: str = recipient_address
		self.value: int = value

	def check_validity(self) -> bool:
		return self.value > 0

	def to_dict(self):
		return collections.OrderedDict({
			'recipient_address': self.recipient_address,
			'value': self.value
		})

	def to_json(self):
		return json.dumps(self.to_dict(), sort_keys=True).encode('utf-8')

	def __repr__(self):
		return self.to_json()

	def __str__(self):
		return self.__repr__()


class Transaction:
	def __init__(self, sender: str = "", inputs: List[TransactionInput] = None, outputs: List[TransactionOutput] = None):
		self.sender = sender or ""  # Alternative -> Sender could be found dynamically by getting first transaction output?
		self.inputs: List[TransactionInput] = inputs or []
		self.outputs: List[TransactionOutput] = outputs or []
		self.timestamp = time.time()
		self.signature = None

	def calculate_input(self, chain) -> int:
		return sum([inp.real_balance(chain) for inp in self.inputs])	# TODO: Possible bug, Must filter out -1??

	def calculate_output(self) -> int:
		return sum([out.value for out in self.outputs])

	def calculate_transaction_fee(self, chain) -> int:
		return self.calculate_input(chain) - self.calculate_output()

	def sign_transaction(self, sender):
		if not isinstance(sender, Nodes.Client):
			raise ValueError("Expected the sender to be a client!")

		signer = sender.signer

		self.signature = None
		h = SHA256.new(self.to_json())
		self.signature = binascii.hexlify(signer.sign(h)).decode('ascii')

	def verify_signature(self) -> bool:
		"""
		:return: Whether the signature belongs to the actual sender or not
		"""
		signature = self.signature
		result = False
		try:
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

	def check_validity(self, chain) -> bool:
		if not self.verify_signature():
			print("WRONG SIGNATURE")
			return False

		if not self.calculate_transaction_fee(chain) >= 0:				# Output is more than available input
			print("Transaction fee negative")
			return False

		return True						 				# TODO: Check previous blocks!

	def print_transaction(self):
		print(json.dumps(self.to_dict(), sort_keys=True, indent=4))
		# print("sender: \t", self.sender)
		# print("inputs: \t", list(map(lambda o: o.to_dict(), self.inputs)))
		# print('outputs: \t', list(map(lambda o: o.to_dict(), self.outputs)))
		# print("time: \t", str(self.timestamp))
		# print("signature: \t", str(self.signature))

	def to_dict(self):
		return collections.OrderedDict({
			'inputs': list(map(lambda o: o.to_dict(), self.inputs)),
			'outputs': list(map(lambda o: o.to_dict(), self.outputs)),
			'timestamp': self.timestamp,
			'signature': self.signature,
		})

	def to_json(self):
		return json.dumps(self.to_dict(), sort_keys=True).encode('utf-8')

	def __repr__(self):
		return self.to_json()

	def __str__(self):
		return self.__repr__()


# class TransactionManager:
# 	def __init__(self):
# 		self.transactions = []
#
# 	def add_transaction(self, transaction) -> bool:
# 		# if not isinstance(transaction, Transaction):
# 		# 	raise ValueError("Transaction is not a valid Transaction object!")
#
# 		if transaction.check_validity():
# 			self.transactions.append(transaction)  # TODO:
# 			return True
# 		print("ERROR -> INVALID TRANSACTION, ", transaction.check_validity())
#
# 		return False
#
# 	def broadcast_transaction(self):  # TODO: Broadcast Transaction
# 		pass
#
# 	def clean_transactions(self):
# 		pass


if __name__ == '__main__':
	print('--- Transaction check ---')
	# clientA = Nodes.Client(Nodes.KeyFactory.create_key())
	# clientB = Nodes.Client(Nodes.KeyFactory.create_key())
	miner = Nodes.Miner(Nodes.KeyFactory.create_key())

	miner.blockchain.dump_blockchain()
	t0 = Transaction(
		miner.identity,
		[
			TransactionInput(0, 0, 0)
		],
		[
			TransactionOutput(miner.identity, 20),
			TransactionOutput(miner.identity, 25)
		]
	)
	t0.sign_transaction(miner)
	miner.add_transaction(t0)
	miner.mine()
	miner.blockchain.dump_blockchain()

	# in0 = TransactionInput()
	# t0 = ATransaction(clientA.identity, [], [])
	# t0.sign_transaction(clientA)
	#
	# print(t0.__dict__)
