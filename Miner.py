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
