UniCoins = []


def dump_blockchain(self):
	print("Number of blocks in the chain: " + str(len(self)))
	for x in range(len(UniCoins)):
		block_temp = UniCoins[x]
		print("block # " + str(x))
		for transaction in block_temp.verified_transactions:
			transaction.display_transaction()
			print('--------------')
		print('=====================================')
