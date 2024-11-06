from setuptools import setup, find_packages

setup(
    name="openergo",
    version="0.1",
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        "click",
        "kombu"
    ],
    entry_points={
        "console_scripts": [
            "openergo = openergo.cli:main",
        ],
    },
)
