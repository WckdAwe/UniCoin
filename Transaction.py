# import binascii
# import datetime
# import collections
# from Crypto.Hash import SHA
# from Client import Client
#
#
# transactions = []
# GENESIS_ADDRESS = "Genesis"
#
#
# class Transaction:
# 	def __init__(self, sender, recipient: Client, value):
# 		self.sender = sender
# 		self.recipient = recipient
# 		self.value = value
# 		self.time = datetime.datetime.now()
#
# 	def to_dict(self):
# 		identity = GENESIS_ADDRESS
# 		if isinstance(self.sender, Client):
# 			identity = self.sender.identity
#
# 		return collections.OrderedDict({
# 			'sender': identity,
# 			'recipient': self.recipient.identity,
# 			'value': self.value,
# 			'time': self.time})
#
# 	def sign_transaction(self):
# 		if not isinstance(self.sender, Client):
# 			raise ValueError("Expected the sender to be a client!")
#
# 		signer = self.sender.signer
# 		h = SHA.new(str(self.to_dict()).encode('utf8'))
# 		return binascii.hexlify(signer.sign(h)).decode('ascii')
#
# 	def print_transaction(self):
# 		print("sender: \t", self.sender)
# 		print("recipient: \t", self.recipient.identity)
# 		print("value: \t", str(self.value))
# 		print("time: \t", str(self.time))
#
#
# def dump_transactions():
# 	for transaction in transactions:
# 		transaction.print_transaction()
# 		print('--------------')
#
#
# if __name__ == '__main__':
# 	clientA = Client()
# 	clientB = Client()
# 	clientC = Client()
# 	clientD = Client()
#
# 	t1 = Transaction(
# 		clientA,
# 		clientB,
# 		5.0
# 	)
# 	t1.sign_transaction()
# 	transactions.append(t1)
#
# 	t2 = Transaction(
# 		clientB,
# 		clientC,
# 		3.0
# 	)
# 	t2.sign_transaction()
# 	transactions.append(t2)
# 	t3 = Transaction(
# 		clientC,
# 		clientD,
# 		4.0
# 	)
# 	t3.sign_transaction()
# 	transactions.append(t3)
# 	t4 = Transaction(
# 		clientA,
# 		clientC,
# 		5.0
# 	)
# 	t4.sign_transaction()
# 	transactions.append(t4)
# 	t5 = Transaction(
# 		clientA,
# 		clientD,
# 		5.0
# 	)
#
# 	dump_transactions()
