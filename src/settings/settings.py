import os

import pytz

from src.api.middleware.custom_exceptions.JWTKeyNotSet import JWTKeyNotSet


def load_env_with_default(env_name: str, default_value):
    if env_name in os.environ:
        env_value = os.environ[env_name]
        if env_value.lower() == 'true':
            return True
        if env_value.lower() == 'false':
            return False
        return env_value
    else:
        return default_value


# Database

DATABASE_USERNAME = load_env_with_default('DATABASE_USERNAME', 'root')
DATABASE_PASSWORD = load_env_with_default('DATABASE_PASSWORD', 'not set')
DATABASE = load_env_with_default('DATABASE', 'fastapi_app')
DATABASE_HOST = load_env_with_default('DATABASE_HOST', 'mysql')
DATABASE_PORT = load_env_with_default('DATABASE_PORT', 3306)

RUN_IN_DOCKER_COMPOSE = load_env_with_default('RUN_IN_DOCKER_COMPOSE',
                                              False)  # env. is always as string --> no boolean without parsing

if RUN_IN_DOCKER_COMPOSE:
    SQLALCHEMY_DATABASE_URI = f"{DATABASE_HOST}+pymysql://{DATABASE_USERNAME}:{DATABASE_PASSWORD}@host.docker.internal:{DATABASE_PORT}/{DATABASE}"
else:
    SQLALCHEMY_DATABASE_URI = f"{DATABASE_HOST}+pymysql://{DATABASE_USERNAME}:{DATABASE_PASSWORD}@localhost:{DATABASE_PORT}/{DATABASE}"

# JWT Token encryption/decryption

ALGORITHM = load_env_with_default('ALGORITHM', 'HS256')
TOKEN_EXPIRE_MINS = int(load_env_with_default('TOKEN_EXPIRE_MINS', 30))
REFRESH_TOKEN_EXPIRE_HOURS = int(load_env_with_default('REFRESH_TOKEN_EXPIRE_HOURS', 10))
TIMEZONE = load_env_with_default('TIMEZONE', pytz.timezone('CET'))
SECRET_KEY = load_env_with_default('SECRET_KEY', 'key not set')

if SECRET_KEY == 'key not set':
    raise JWTKeyNotSet()
    # If Private Key for JWT is not set, crash the complete service because it's a major security risk
