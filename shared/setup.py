from setuptools import setup, find_packages

setup(
    name="shared",
    version="0.1.0",
    packages=find_packages(),
    install_requires=[
        "fastapi",
        "sqlalchemy",
        "pydantic",
        "loguru",
        "slowapi",
        "passlib[bcrypt]",
        "aio-pika",
        "python-jose[cryptography]",
        "redis[hiredis]",
    ],
)
