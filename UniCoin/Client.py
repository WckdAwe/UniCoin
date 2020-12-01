# import binascii
# import Crypto
# import Crypto.Random
# from Crypto.PublicKey import RSA
# from Crypto.Signature import pkcs1_15
#
#
# class Client:
#
#     def __init__(self):
#         random = Crypto.Random.new().read
#         self.__private_key = RSA.generate(1024, random)
#         self.public_key = self.__private_key.publickey()
#         self.signer = pkcs1_15.new(self.__private_key)
#
#     @property
#     def identity(self) -> str:
#         return binascii.hexlify(self.public_key.exportKey(format='DER')).decode('ascii')
#
#     def __str__(self):
#         return self.identity
#
#
# if __name__ == '__main__':
#     clientA = Client()
#     print(clientA.identity)
