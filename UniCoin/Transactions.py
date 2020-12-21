import hashlib
import json
import collections
import time
import binascii

from typing import List, Tuple
from Crypto.Hash import SHA256
from Crypto.PublicKey import RSA
from Crypto.Signature import pkcs1_15

import UniCoin.Nodes as Nodes
import UniCoin.Blockchain as Blockchain

import logging
log = logging.getLogger('werkzeug')


class TransactionInput:
	def __init__(self, block_index: int, transaction_index: int, output_index: int, balance: int = None):
		self.block_index: int = block_index
		self.transaction_index: int = transaction_index
		self.output_index: int = output_index

		# Helper variables to avoid unnecessary calculations
		self.__balance: int = balance or -1

	@property
	def balance(self) -> int:
		return self.__balance

	def is_coinbase(self) -> bool:
		return self.block_index == 0 and self.transaction_index == 0 and self.output_index == 0

	def find_transaction(self, chain):
		try:
			block: Blockchain.Block = chain[self.block_index]

			# TODO: Change this when adding TRANSACTIONS
			transaction = block.verified_transactions[self.transaction_index]
			return transaction.outputs[self.output_index]
		except Exception:
			return None

	def check_validity(self, sender: str, chain) -> bool:
		"""
		:param sender:
		:param chain:
		:return:
		"""
		output = self.find_transaction(chain)
		if output is None:
			log.debug(f'[TRANSACTION IN] Validation failed (NON-EXISTENT).')
			return False

		if output.value <= 0:
			log.debug(f'[TRANSACTION IN] Validation failed (NEGATIVE VALUE).')
			return False

		if output.recipient_address != sender:
			log.debug(f'[TRANSACTION IN] Validation failed (BAD-SENDER).')
			return False

		self.__balance = output.value  # Cache the balance

		return True

	@property
	def hash(self) -> str:
		return hashlib.md5(self.to_json()).hexdigest()

	def to_dict(self):
		return collections.OrderedDict({
			'block_index': self.block_index,
			'transaction_index': self.transaction_index,
			'output_index': self.output_index})

	def to_json(self, indent=None) -> bytes:
		return json.dumps(self.to_dict(), sort_keys=True, indent=indent).encode('utf-8')

	def __repr__(self):
		return self.to_json()

	def __str__(self):
		return str(self.to_json(indent=4).decode('utf-8'))

	def __hash__(self):
		return hash((self.block_index, self.transaction_index, self.output_index))

	def __eq__(self, other):
		if not isinstance(other, TransactionInput):
			return NotImplemented

		return self.block_index == other.block_index and self.transaction_index == other.transaction_index and \
			   self.output_index == other.output_index

	@classmethod
	def from_json(cls, data):
		block_index = int(data["block_index"])
		transaction_index = int(data["transaction_index"])
		output_index = int(data["output_index"])
		return cls(
			block_index=block_index,
			transaction_index=transaction_index,
			output_index=output_index
		)


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

	def to_json(self, indent=None):
		return json.dumps(self.to_dict(), sort_keys=True, indent=indent).encode('utf-8')

	def __repr__(self):
		return self.to_json()

	def __str__(self):
		return str(self.to_json(indent=4).decode('utf-8'))

	def __hash__(self):
		return hash((self.recipient_address, self.value))

	@classmethod
	def from_json(cls, data):
		recipient_address = str(data["recipient_address"])
		value = int(data["value"])
		return cls(
			recipient_address=recipient_address,
			value=value
		)


class Transaction:
	def __init__(self, sender: str = "", inputs: Tuple[TransactionInput] = (), outputs: Tuple[TransactionOutput] = (),
				 timestamp: float = None, signature: str = None):
		self.sender = sender  # Alternative -> Sender could be found dynamically by getting first transaction output?
		self.inputs: Tuple[TransactionInput] = inputs
		self.outputs: Tuple[TransactionOutput] = outputs
		self.timestamp = timestamp or time.time()
		self.signature = signature

		# Helper variables to avoid unnecessary calculations
		self.__balance_input: int = -1
		self.__transaction_fee: int = -1

	@property
	def balance_input(self) -> int:
		return self.__balance_input

	@property
	def transaction_fee(self) -> int:
		return self.__transaction_fee

	@property
	def balance_output(self) -> int:
		return sum([out.value for out in self.outputs])

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
			self.signature = None									# Remove signature to verify hash

			der_key = binascii.unhexlify(self.sender)
			sig = binascii.unhexlify(signature)

			public_key = RSA.import_key(der_key)
			h = SHA256.new(self.to_json())

			signer = pkcs1_15.new(public_key)
			signer.verify(h, sig)									# Verify that the hash and transaction match
			result = True
		except (ValueError, TypeError, Exception):
			result = False
		finally:
			self.signature = signature								# Reset signature
			return result

	def __calculate_input(self) -> int:
		self.__balance_input = sum([inp.balance for inp in self.inputs])
		return self.__balance_input

	def __calculate_transaction_fee(self) -> int:
		self.__transaction_fee = self.__calculate_input() - self.balance_output
		return self.__transaction_fee

	def check_validity(self, chain) -> bool:
		if not self.verify_signature():
			log.debug(f'[TRANSACTION] Validation failed (SIGNATURE): \'{self.hash}\'')
			return False

		for inp in self.inputs:
			if not inp.check_validity(self.sender, chain):
				log.debug(f'[TRANSACTION] Validation failed (INPUTS): \'{self.hash}\'')
				return False

		for out in self.outputs:
			if not out.check_validity():
				log.debug(f'[TRANSACTION] Validation failed (OUTPUTS): \'{self.hash}\'')
				return False

		if not self.__calculate_transaction_fee() >= 0:			    # Output is more than available input
			log.debug(f'[TRANSACTION] Validation failed (TRANSACTION FEE - NEGATIVE): \'{self.hash}\'')
			return False

		return True						 							# TODO: Check previous blocks!

	@property
	def hash(self) -> str:
		return hashlib.md5(self.to_json()).hexdigest()

	def to_dict(self):
		return collections.OrderedDict({
			'sender': self.sender,
			'inputs': tuple(map(lambda o: o.to_dict(), self.inputs)),
			'outputs': tuple(map(lambda o: o.to_dict(), self.outputs)),
			'timestamp': self.timestamp,
			'signature': self.signature,
		})

	def to_json(self, indent=None):
		return json.dumps(self.to_dict(), sort_keys=True, indent=indent).encode('utf-8')

	def __repr__(self):
		return self.to_json()

	def __str__(self):
		return str(self.to_json(indent=4).decode('utf-8'))

	def __hash__(self):
		return hash((self.sender, self.inputs, self.outputs, self.timestamp, self.signature))

	@classmethod
	def from_json(cls, data):
		sender = str(data["sender"])
		inputs = tuple(map(TransactionInput.from_json, data["inputs"]))
		outputs = tuple(map(TransactionOutput.from_json, data["outputs"]))
		timestamp = float(data["timestamp"])
		signature = str(data["signature"])
		return cls(
			sender=sender,
			inputs=inputs,
			outputs=outputs,
			timestamp=timestamp,
			signature=signature
		)
