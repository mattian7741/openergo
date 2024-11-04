from setuptools import setup, find_packages



# Define the setup parameters
setup(
    name='openergo',
    version='0.0.1',  # Enclose the version number in quotes
    description='Project for service bus',
    long_description_content_type='text/markdown',
    packages=find_packages(),
    install_requires=[
        "pyyaml",
	    "pydash",
        "graphviz",
        "dill",
        "cryptography",
        "line-profiler",
        "click",
        "ansicolors",
        "click-default-group"
    ],
    entry_points={
        "console_scripts": [
            "openergo=openergo.openergo_click:main"
        ]
    },

)
