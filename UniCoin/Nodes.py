import binascii
import os
import uuid

import Crypto
from Crypto.PublicKey import RSA
from Crypto.PublicKey.RSA import RsaKey
from Crypto.Signature import pkcs1_15
from Crypto.Signature.pkcs1_15 import PKCS115_SigScheme

from UniCoin import paths


class Client:
	def __init__(self, private_key: RsaKey):
		self.private_key: RsaKey = private_key
		self.public_key: RsaKey = self.private_key.publickey()
		self.signer: PKCS115_SigScheme = pkcs1_15.new(self.private_key)
		self.UTX = [] 	# List of unspent transactions

	def create_transaction(self):
		pass

	@property
	def identity(self) -> str:
		return binascii.hexlify(self.public_key.exportKey(format='DER')).decode('ascii')

	def __str__(self):
		return self.identity


class Miner(Client):
	def __init__(self, private_key: RsaKey):
		super().__init__(private_key)

	def mine(self):
		pass


class Network:
	def __init__(self):
		self._nodes = set()

	def register_node(self, address: str):
		self._nodes.add(address)

	def blacklist_node(self, address: str):		# TODO: Is this possible for a blockchain network??
		pass


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
