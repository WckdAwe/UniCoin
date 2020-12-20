from flask import Flask
import UniCoin.helpers.menus as menus
import UniCoin.Nodes as Nodes
import threading
app = Flask(__name__)
my_node: Nodes.Node = None


def run(port=5000):
	global my_node
	key = menus.menu_select_key()
	my_node = menus.menu_select_client_type(key)
	my_node.network = Nodes.PeerNetwork(
		my_peer=Nodes.Peer("127.0.0.1", port)
	)
	print('Good to go... Starting web server...')
	import UniCoin.web

	w = threading.Thread(target=app.run, args=(None, port,), daemon=True)
	w.start()

	while True:
		menus.menu_main(my_node)


def tst_run(port=5000):
	global my_node
	my_node = Nodes.Miner(Nodes.KeyFactory.create_key())

	import UniCoin.web
	app.run(port=port)
