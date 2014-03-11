from setuptools import setup

setup(
    name = 'disasters',
    packages = ['disasters'],
    version = '0.0.2',
    description = 'A python library for my research on disaster news.',
    author='Chris Kedzie',
    author_email='kedzie@cs.columbia.edu',
    url='https://github.com/kedz/disasters',
    install_requires=[
        'corenlp',
    ]

)

