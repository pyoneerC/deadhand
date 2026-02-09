# SPDX-License-Identifier: BUSL-1.1
# Copyright (c) 2026 pyoneerC. All rights reserved.
"""
Simple AES-GCM encryption for shard_c storage.
Key is derived from each user's unique heartbeat_token.
No external key management needed.
"""
import os
import base64
import hashlib
from cryptography.hazmat.primitives.ciphers.aead import AESGCM


def derive_key(heartbeat_token: str) -> bytes:
    """Derive a 256-bit AES key from the heartbeat token."""
    return hashlib.sha256(heartbeat_token.encode()).digest()


def encrypt_shard(shard: str, heartbeat_token: str) -> str:
    """
    Encrypt shard using AES-GCM with key derived from heartbeat_token.
    Returns base64-encoded ciphertext (nonce || ciphertext).
    """
    key = derive_key(heartbeat_token)
    aesgcm = AESGCM(key)
    
    # Generate random 12-byte nonce
    nonce = os.urandom(12)
    
    # Encrypt
    ciphertext = aesgcm.encrypt(nonce, shard.encode(), None)
    
    # Combine nonce + ciphertext and base64 encode
    encrypted = base64.b64encode(nonce + ciphertext).decode()
    return encrypted


def decrypt_shard(encrypted_shard: str, heartbeat_token: str) -> str:
    """
    Decrypt shard using AES-GCM with key derived from heartbeat_token.
    Expects base64-encoded string (nonce || ciphertext).
    """
    key = derive_key(heartbeat_token)
    aesgcm = AESGCM(key)
    
    # Decode base64
    data = base64.b64decode(encrypted_shard)
    
    # Extract nonce (first 12 bytes) and ciphertext
    nonce = data[:12]
    ciphertext = data[12:]
    
    # Decrypt
    plaintext = aesgcm.decrypt(nonce, ciphertext, None)
    return plaintext.decode()


def encrypt_token(token: str, master_key: str) -> str:
    """
    Encrypt a sensitive token (like heartbeat_token) using the server MASTER_KEY.
    Protects against database leaks.
    """
    # Master key must be 32 bytes (256 bits)
    # If string is provided, we hash it to get 32 bytes
    if isinstance(master_key, str):
        key = hashlib.sha256(master_key.encode()).digest()
    else:
        key = master_key
        
    aesgcm = AESGCM(key)
    nonce = os.urandom(12)
    ciphertext = aesgcm.encrypt(nonce, token.encode(), None)
    return base64.b64encode(nonce + ciphertext).decode()


def decrypt_token(encrypted_token: str, master_key: str) -> str:
    """
    Decrypt a sensitive token using the server MASTER_KEY.
    """
    if isinstance(master_key, str):
        key = hashlib.sha256(master_key.encode()).digest()
    else:
        key = master_key
        
    aesgcm = AESGCM(key)
    
    try:
        data = base64.b64decode(encrypted_token)
        nonce = data[:12]
        ciphertext = data[12:]
        plaintext = aesgcm.decrypt(nonce, ciphertext, None)
        return plaintext.decode()
    except Exception:
        # Fallback: maintain backward compatibility for unencrypted tokens
        # If decryption fails (e.g. invalid base64, tag mismatch, or old plain token),
        # return the raw string as is.
        # This allows seamless migration for existing tokens.
        return encrypted_token

