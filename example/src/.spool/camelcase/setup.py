from setuptools import setup, find_packages

setup(
    name="camelcase",
    version="0.1",
    packages=find_packages(),
    include_package_data=True,
    install_requires=[],
    entry_points={
        'console_scripts': [
            'camelcase = camelcase.__main__:main',
        ],
    },
)