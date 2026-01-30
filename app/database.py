# SPDX-License-Identifier: BUSL-1.1
# Copyright (c) 2026 pyoneerC. All rights reserved.

import os
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv

load_dotenv()

# Database configuration
# Priority: Postgres (production) > SQLite (local dev)

DATABASE_URL = os.getenv("DATABASE_URL")

if DATABASE_URL and DATABASE_URL.startswith("postgresql"):
    # Production: Neon/Vercel Postgres
    engine = create_engine(DATABASE_URL, pool_pre_ping=True)
    print("🐘 Connected to Neon Postgres (Production)")
elif DATABASE_URL and DATABASE_URL.startswith("postgres://"):
    # Fix old postgres:// prefix for SQLAlchemy
    fixed_url = DATABASE_URL.replace("postgres://", "postgresql://", 1)
    engine = create_engine(fixed_url, pool_pre_ping=True)
    print("🐘 Connected to Postgres (Production)")
else:
    # Local development: SQLite
    DB_PATH = "sqlite:///./Deadhand.db"
    engine = create_engine(DB_PATH, connect_args={"check_same_thread": False})
    print("💾 Using local SQLite database")

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()
