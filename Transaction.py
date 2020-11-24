import hashlib
import random
import string
import json
import binascii
import numpy as np
import pandas as pd
import logging
import datetime
import collections
import Crypto
import Crypto.Random
from Crypto.Hash import SHA
from Crypto.PublicKey import RSA
from Crypto.Signature import PKCS1_v1_5
from Client import Client


transactions = []


class Transaction:
	def __init__(self, sender, recipient, value):
		self.sender = sender
		self.recipient = recipient
		self.value = value
		self.time = datetime.datetime.now()

	def to_dict(self):
		if self.sender == "Genesis":
			identity = "Genesis"
		else:
			identity = self.sender.identity

		return collections.OrderedDict({
			'sender': identity,
			'recipient': self.recipient,
			'value': self.value,
			'time': self.time})

	def sign_transaction(self):
		private_key = self.sender._private_key
		signer = PKCS1_v1_5.new(private_key)
		h = SHA.new(str(self.to_dict()).encode('utf8'))
		return binascii.hexlify(signer.sign(h)).decode('ascii')

	def print_transaction(self):
		print("sender: ", self.sender)
		print("recipient: ", self.recipient)
		print("value: ", str(self.value))
		print("time: ", str(self.time))


def dump_transactions():
	for transaction in transactions:
		transaction.print_transaction()
		print('--------------')


if __name__ == '__main__':
	Dinesh = Client()
	Ramesh = Client()
	Seema = Client()
	Vijay = Client()

	t1 = Transaction(
		Dinesh,
		Ramesh.identity,
		15.0
	)
	t1.sign_transaction()
	transactions.append(t1)

	t2 = Transaction(
		Dinesh,
		Seema.identity,
		6.0
	)
	t2.sign_transaction()
	transactions.append(t2)
	t3 = Transaction(
		Ramesh,
		Vijay.identity,
		2.0
	)
	t3.sign_transaction()
	transactions.append(t3)
	t4 = Transaction(
		Seema,
		Ramesh.identity,
		4.0
	)
	t4.sign_transaction()
	transactions.append(t4)
	t5 = Transaction(
		Vijay,
		Seema.identity,
		7.0
	)
	t5.sign_transaction()
	transactions.append(t5)
	t6 = Transaction(
		Ramesh,
		Seema.identity,
		3.0
	)
	t6.sign_transaction()
	transactions.append(t6)
	t7 = Transaction(
		Seema,
		Dinesh.identity,
		8.0
	)
	t7.sign_transaction()
	transactions.append(t7)
	t8 = Transaction(
		Seema,
		Ramesh.identity,
		1.0
	)
	t8.sign_transaction()
	transactions.append(t8)
	t9 = Transaction(
		Vijay,
		Dinesh.identity,
		5.0
	)
	t9.sign_transaction()
	transactions.append(t9)
	t10 = Transaction(
		Vijay,
		Ramesh.identity,
		3.0
	)
	t10.sign_transaction()
	transactions.append(t10)

	dump_transactions()
