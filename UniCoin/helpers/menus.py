from Crypto.PublicKey.RSA import RsaKey


def menu_select_client_type(private_key):
	import UniCoin.Nodes as Nodes

	print('-'*23, ' [UNICOIN - Select Client Type] ', '-'*23)
	print('1. Client')
	print('2. Miner')
	print('0. Exit')

	while True:
		inp = int(input('Selection: '))
		if inp not in range(0, 3):
			print('Incorrect input. Try again.')
			continue
		break

	if inp == 0:
		exit(0)
	elif inp == 1:
		return Nodes.Client(private_key)
	else:
		return Nodes.Miner(private_key)


def menu_generate_key() -> RsaKey:
	import UniCoin.Nodes as Nodes

	print('-'*23, ' [UNICOIN - Friendly name] ', '-'*23)
	print('Select a friendly name for your key.')
	print('Just try not to override any previous one and lose fortunes ^_^.')
	inp = str(input('Friendly name (Keep empty for random): '))
	key = Nodes.KeyFactory.create_key()
	Nodes.KeyFactory.store_key(key, inp)
	return key


def menu_select_key() -> RsaKey:
	import UniCoin.Nodes as Nodes
	import UniCoin.helpers as helpers
	import os

	try:
		path = helpers.paths.PATH_WALLETS
		addresses = [name.removesuffix('.der') for name in os.listdir(path) if os.path.isfile(os.path.join(path, name))]
	except Exception:
		addresses = []

	print('-'*23, ' [UNICOIN - Select address] ', '-'*23)
	print('1. Generate new address')
	for idx, address in enumerate(addresses):
		print(f'{idx+2}. {address}')
	print('0. Exit')

	while True:
		inp = int(input('Selection: '))
		if inp not in range(0, len(addresses)+2):
			print('Incorrect input. Try again.')
			continue
		break

	if inp == 0:
		exit(0)
	elif inp == 1:
		return menu_generate_key()
	else:
		return Nodes.KeyFactory.load_key(addresses[inp-2])
