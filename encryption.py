import nacl.utils
import nacl.secret
import nacl.encoding
import nacl.pwhash
from nacl import encoding
from nacl.public import PrivateKey, Box
from system import System
from keypair import KeyPair


class Encryption:

    def __init__(self):
        self.system = System()

    """
    liefert den schlüssel zum symmetrischen verschlüsseln
    """

    def get_sym_key(self):
        return self.system.read_file("sym.key")

    """
    symmetrische verschlüsselungsmethode
    """

    def encrypt(self, data):
        try:
            box = nacl.secret.SecretBox(self.get_sym_key())
            return nacl.encoding.Base64Encoder.encode(box.encrypt(data))
        except Exception as error:
            self.system.log_exception(error)
            return False

    """
    symmetrische entschlüsselungsmethode
    """

    def decrypt(self, data):
        try:
            box = nacl.secret.SecretBox(self.get_sym_key())
            return box.decrypt(nacl.encoding.Base64Encoder.decode(data))
        except Exception as error:
            self.system.log_exception(error)
            return False

    """
    liefert einen password hash zurück (argon2id)
    """

    def hash_password(self, password):
        return nacl.pwhash.argon2id.str(password.encode())

    """
    schreibt alle benötigten schlüssel auf die festplatte
    """

    def setup_sym_key(self):
        try:
            sym_key = nacl.utils.random(nacl.secret.SecretBox.KEY_SIZE)
            self.system.write_file("sym.key", sym_key, True)
            return True
        except Exception as error:
            self.system.log_exception(error)
            return False

    def setup_async_keys(self):
        private_key = PrivateKey.generate()
        public_key = private_key.public_key
        self.system.write_file("pub.key", public_key.encode(encoder=encoding.RawEncoder), True)
        self.system.write_file("priv.key", private_key.encode(encoder=encoding.RawEncoder), True)

    def as_base_64(self, data):
        return nacl.encoding.Base64Encoder.encode(data)

    def get_key_pair(self):
        secret_key = PrivateKey.generate()
        public_key = secret_key.public_key
        public_key_encrypted = self.encrypt(public_key.encode(encoder=encoding.RawEncoder))
        private_key_encrypted = self.encrypt(secret_key.encode(encoder=encoding.RawEncoder))
        key_pair = KeyPair()
        key_pair.set_private_key(private_key_encrypted)
        key_pair.set_public_key(public_key_encrypted)
        return key_pair
