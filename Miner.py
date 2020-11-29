import hashlib

last_transaction_index = 0


def sha256(message):
	return hashlib.sha256(message.encode('ascii')).hexdigest()


def mine(message, difficulty=1):
	assert difficulty >= 1
	prefix = '1' * difficulty
	for i in range(1000):
		digest = sha256(str(hash(message)) + str(i))
		if digest.startswith(prefix):
			print("after " + str(i) + " iterations found nonce: " + digest)
			return digest

	print("Sadness")


if __name__ == '__main__':
	mine("test message", 1)
	print("done!")

	block = Block()
	for i in range(3):
		temp_transaction = transactions[last_transaction_index]
		# validate transaction
		# if valid
		block.verified_transactions.append (temp_transaction)
		last_transaction_index += 1

	block.previous_block_hash = last_block_hash
	block.Nonce = mine (block, 2)
	digest = hash (block)
	UniCoins.append (block)
	last_block_hash = digest

	# Miner 2 adds a block
	block = Block()

	for i in range(3):
		temp_transaction = transactions[last_transaction_index]
		# validate transaction
		# if valid
		block.verified_transactions.append (temp_transaction)
	last_transaction_index += 1
	block.previous_block_hash = last_block_hash
	block.Nonce = mine (block, 2)
	digest = hash (block)
	UniCoins.append (block)
	last_block_hash = digest

	dump_blockchain(UniCoins)
