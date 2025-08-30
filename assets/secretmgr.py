from cryptography.fernet import Fernet
from cryptography.hazmat.primitives.asymmetric import rsa, padding
from cryptography.hazmat.primitives import serialization, hashes
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes

import base64
import keyring
import os


class SecretMgr:
    def __init__(self):
        pass

    def make_msg_keys(self, private = None):
        "Create public and private keys"

        if not private:
            private = rsa.generate_private_key(
                public_exponent=65537, key_size=2048
            )

        public = private.public_key()

        pem = public.public_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PublicFormat.SubjectPublicKeyInfo
        ).decode()

        return private, pem

    def make_data_key(self):
        "Creates data file key"

        key = Fernet.generate_key()

        keyring.set_password(
            "NixChat", "user", key.decode()
        )

        return key

    def get_data_key(self):
        "Returns data file key"
        
        key = keyring.get_password(
            "NixChat", "user"
        )

        if not key:
            key = self.make_data_key()

        return key

    def save_data(self, data, path: str):
        "Saves data to some file"

        fernet = Fernet(self.get_data_key())

        enc_data = fernet.encrypt(data.encode())

        with open(path, "wb") as f:
            f.write(enc_data)
        

    def load_data(self, path: str):
        "Loads data from file"

        fernet = Fernet(self.get_data_key())

        with open(path, "rb") as f:
            enc_data = f.read()

        data = fernet.decrypt(enc_data)

        return data

    def encrypt_by_pem(self, data, pem) -> str:
        "Encrypts data by PEM"

        data = data.encode()
        public_key = serialization.load_pem_public_key(pem.encode())
        
        aes_key = os.urandom(32)
        iv = os.urandom(16)
        
        cipher = Cipher(algorithms.AES(aes_key), modes.CFB(iv))
        encryptor = cipher.encryptor()
        encrypted_data = encryptor.update(data) + encryptor.finalize()
        
        encrypted_aes_key = public_key.encrypt(
            aes_key,
            padding.OAEP(
                mgf=padding.MGF1(algorithm=hashes.SHA256()),
                algorithm=hashes.SHA256(),
                label=None
            )
        )
        
        return base64.b64encode(encrypted_aes_key + iv + encrypted_data).decode()
    
    def decrypt_by_pk(self, b64_data, key) -> bytes:
        "Decrypts base64 encoded data"

        encrypted_data = base64.b64decode(b64_data)

        rsa_key_size = key.key_size // 8
        encrypted_aes_key = encrypted_data[:rsa_key_size]
        iv = encrypted_data[rsa_key_size:rsa_key_size+16]
        ciphertext = encrypted_data[rsa_key_size+16:]
        
        aes_key = key.decrypt(
            encrypted_aes_key,
            padding.OAEP(
                mgf=padding.MGF1(algorithm=hashes.SHA256()),
                algorithm=hashes.SHA256(),
                label=None
            )
        )
        
        cipher = Cipher(algorithms.AES(aes_key), modes.CFB(iv))
        decryptor = cipher.decryptor()
        return decryptor.update(ciphertext) + decryptor.finalize()
