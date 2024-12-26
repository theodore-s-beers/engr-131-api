import base64
import os

import nacl.public

private_key_path = ".server_private_key.bin"
public_key_path = ".server_public_key.bin"

if os.path.exists(private_key_path) or os.path.exists(public_key_path):
    print("A key already exists at one of the specified paths")

    if os.path.exists(public_key_path):
        with open(public_key_path, "rb") as f:
            public_key = nacl.public.PublicKey(f.read())
            key_b64 = base64.b64encode(public_key.encode())
            key_str = key_b64.decode()
            print("Server public key:", key_str)

    exit()

# Generate keypair
private_key = nacl.public.PrivateKey.generate()
public_key = private_key.public_key

# Save keys to files
with open(private_key_path, "wb") as f:
    f.write(private_key.encode())
with open(public_key_path, "wb") as f:
    f.write(public_key.encode())

print("Generated and saved server keypair")

public_key_b64 = base64.b64encode(public_key.encode())
public_key_str = public_key_b64.decode()
print("Server public key:", public_key_str)
