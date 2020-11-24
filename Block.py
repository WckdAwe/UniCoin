from Client import Client
from Transaction import Transaction

UniCoins = []


class Block:
	verified_transactions: list[Transaction]

	def __init__(self):
		self.verified_transactions: list[Transaction] = []
		self.previous_block_hash: str = ""
		self.Nonce: str = ""


def dump_blockchain(self):
	print("Number of blocks in the chain: " + str(len(self)))
	for x in range(len(UniCoins)):
		block_temp = UniCoins[x]
		print("block # " + str(x))
		for transaction in block_temp.verified_transactions:
			transaction.print_transaction()
			print('--------------')
		print('=====================================')


if __name__ == '__main__':
	Dinesh = Client()
	t0 = Transaction(
		"Genesis",
		Dinesh.identity,
		500.0
	)

	block0 = Block()
	block0.previous_block_hash = None
	Nonce = None

	digest = hash(block0)
	last_block_hash = digest

	block0.verified_transactions.append(t0)

	UniCoins.append(block0)
	dump_blockchain(UniCoins)
