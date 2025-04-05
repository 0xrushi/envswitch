from setuptools import setup, find_packages

setup(
    name="envswitch",
    version="0.1.0",
    packages=find_packages(),
    install_requires=[
        "typer",
        "rich",
        "openai",
        "thefuzz",
    ],
    entry_points={
        "console_scripts": [
            "envswitch=envswitch.cli:main",
        ],
    },
)