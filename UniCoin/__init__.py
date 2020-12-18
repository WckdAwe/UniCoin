from flask import Flask
import UniCoin.helpers.menus as menus
import UniCoin.Nodes as Nodes
app = Flask(__name__)
my_node: Nodes.Node = None


def run(port=5000):
	global my_node
	key = menus.menu_select_key()
	my_node = menus.menu_select_client_type(key)
	print('Good to go... Starting web server...')
	menus.menu_main(my_node)

	# import UniCoin.web
	# app.run()


def tst_run(port=5000):
	global my_node
	my_node = Nodes.Miner(Nodes.KeyFactory.create_key())

	import UniCoin.web
	app.run(port=port)
