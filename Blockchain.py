import json
import collections
import datetime

from hashlib import sha256
from Client import Client
from Transaction import Transaction


UniCoins_Chain = []	 	# The blockchain stored in this node
transactions = []		# Available transactions visible to this node

GENESIS_ADDRESS = "Genesis"


class Transaction:
	def __init__(self, sender, recipient: Client, value):
		self.sender = sender
		self.recipient = recipient
		self.value = value
		self.time = datetime.datetime.now()

	def to_dict(self):
		identity = GENESIS_ADDRESS
		if isinstance(self.sender, Client):
			identity = self.sender.identity

		return collections.OrderedDict({
			'sender': identity,
			'recipient': self.recipient.identity,
			'value': self.value,
			'time': self.time})

	def sign_transaction(self):
		if not isinstance(self.sender, Client):
			raise ValueError("Expected the sender to be a client!")

		signer = self.sender.signer
		h = SHA.new(str(self.to_dict()).encode('utf8'))
		return binascii.hexlify(signer.sign(h)).decode('ascii')

	def print_transaction(self):
		print("sender: \t", self.sender)
		print("recipient: \t", self.recipient.identity)
		print("value: \t", str(self.value))
		print("time: \t", str(self.time))

	@staticmethod
	def dump_transactions():
		for transaction in transactions:
			transaction.print_transaction()
			print('--------------')


class Block:

	def __init__(self):
		self.verified_transactions: list[Transaction] = []
		self.previous_block_hash: str = None
		self.Nonce: str = None

	def calculate_hash(self):
		"""
		Returns the hash of the block by converting its instance into a JSON String.
		:return: Hash of the block
		"""

		block_json = json.dumps(self.__dict__, sort_keys=True)  # Must be sorted in-order to avoid different hash generation
		return sha256(block_json.encode()).hexdigest()


class BlockChain:

	@staticmethod
	def dump_blockchain():
		print(f"Number of blocks in the chain: {len(UniCoins)}")
		for x in range(len(UniCoins)):
			block_temp = UniCoins[x]
			print("block # " + str(x))
			for transaction in block_temp.verified_transactions:
				transaction.print_transaction()
				print('--------------')
			print('=====================================')


if __name__ == '__main__':
	clientA = Client()
	t0 = Transaction(
		"Genesis",
		clientA,
		500.0
	)

	block0 = Block()

	block0.verified_transactions.append(t0)

	UniCoins.append(block0)

	BlockChain.dump_blockchain()
