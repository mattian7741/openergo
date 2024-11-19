from setuptools import setup

setup(
    name='openergo',
    version='0.1',
    packages=['openergo'],
    install_requires=[
        "click",
        "graphviz",
        "pydash",
        "dill",
        "cryptography"
    ],
    entry_points={
        "console_scripts": [
            "openergo = openergo.openergo_cli:main",
        ],
    },    
)
