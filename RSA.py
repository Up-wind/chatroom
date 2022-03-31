from Crypto import Random
from Crypto.Hash import SHA
from Crypto.Cipher import PKCS1_v1_5 as Cipher_pkcs1_v1_5
from Crypto.Signature import PKCS1_v1_5 as Signature_pkcs1_v1_5
from Crypto.PublicKey import RSA
import base64

def RSAInit():
    random_generator = Random.new().read
    rsa = RSA.generate(1024, random_generator)
    private_pem = rsa.exportKey()
    public_pem = rsa.publickey().exportKey()
    return private_pem, public_pem, random_generator


def RSAEncode(message, key):
    rsakey = RSA.importKey(key)
    cipher = Cipher_pkcs1_v1_5.new(rsakey)
    cipher_text = base64.b64encode(cipher.encrypt(message))
    return cipher_text


def RSASign(cipher_text, key):
    rsakey = RSA.importKey(key)
    signer = Signature_pkcs1_v1_5.new(rsakey)
    digest = SHA.new()
    digest.update(cipher_text)
    sign = signer.sign(digest)
    signature = base64.b64encode(sign)
    return signature


def RSACheck(cipher_text, signature, key):
    rsakey = RSA.importKey(key)
    verifier = Signature_pkcs1_v1_5.new(rsakey)
    digest = SHA.new()
    # Assumes the data is base64 encoded to begin with
    digest.update(cipher_text)
    is_verify = verifier.verify(digest, base64.b64decode(signature))
    return is_verify


def RSADecode(cipher_text, key, random_generator):
    rsakey = RSA.importKey(key)
    cipher = Cipher_pkcs1_v1_5.new(rsakey)
    text = cipher.decrypt(base64.b64decode(cipher_text), random_generator)
    return text


def main():
    print("No main")

if __name__ == "__main__":
    main()