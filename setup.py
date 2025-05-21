from setuptools import setup, find_packages

setup(
    name="utfgradebot",
    version="0.1",
    packages=find_packages(),
    install_requires=[
        "psycopg2-binary",
        "python-dotenv",
        "selenium",
        "requests",
        "beautifulsoup4"
    ],
) 