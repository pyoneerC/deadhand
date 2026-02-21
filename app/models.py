# SPDX-License-Identifier: BUSL-1.1
# Copyright (c) 2026 pyoneerC. All rights reserved.

from sqlalchemy import Column, Integer, String, DateTime, Boolean, LargeBinary
from sqlalchemy.sql import func
from .database import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True)
    beneficiary_email = Column(String)
    shard_c = Column(String)  # AES-GCM encrypted, key derived from heartbeat_token
    
    # IMMUTABILITY PROTECTION: Hash of original config
    # Hash = SHA256(beneficiary_email + shard_c + created_at)
    # If attacker modifies beneficiary_email, hash won't match
    config_hash = Column(String)  # Immutable commitment
    
    last_heartbeat = Column(DateTime(timezone=True), server_default=func.now())
    is_dead = Column(Boolean, default=False)
    heartbeat_token = Column(String)  # Simple token for authentication via email link
    
    # Stripe subscription tracking
    stripe_customer_id = Column(String, nullable=True, index=True)  # cus_xxx
    stripe_subscription_id = Column(String, nullable=True, index=True)  # sub_xxx (for annual)
    plan_type = Column(String, default="lifetime")  # "annual" or "lifetime"
    is_active = Column(Boolean, default=True)  # False if subscription cancelled
    
    # Telegram fallback for heartbeat notifications
    telegram_chat_id = Column(String, nullable=True)  # Telegram chat ID for notifications
    
    # Passkey (WebAuthn) credentials for passwordless auth
    passkey_credential_id = Column(LargeBinary, nullable=True, unique=True, index=True)
    passkey_public_key = Column(LargeBinary, nullable=True)
    passkey_sign_count = Column(Integer, nullable=True, default=0)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
