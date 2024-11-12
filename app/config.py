# app/config.py
import os

class Config:
    SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URL') or 'sqlite:///booking.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
