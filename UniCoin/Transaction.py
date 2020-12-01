import json
import collections
import time
import binascii

from Crypto.Hash import SHA256
from Crypto.PublicKey import RSA
from Crypto.Signature import pkcs1_15

from UniCoin.Nodes import Client
from UniCoin.decorators import singleton


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
		self.transactions = []

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
