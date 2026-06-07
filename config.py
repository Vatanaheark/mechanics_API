import os

class DevelopmentConfig:
    SQLALCHEMY_DATABASE_URI = 'sqlite:///app.db'
    DEBUG = True
    

class TestingConfig:
    SQLALCHEMY_DATABASE_URI = 'sqlite:///testing.db'
    DEBUG = True
    CACHE_TYPE = 'SimpleCache'


class ProductionConfig:
    DEBUG = False
    SQLALCHEMY_DATABASE_URI = os.getenv("DATABASE_URL")
    SECRET_KEY = os.getenv("SECRET_KEY")
