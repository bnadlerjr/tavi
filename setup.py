from setuptools import setup

setup(
    name='Tavi',
    version='0.1.0',
    author='Bob Nadler Jr.',
    author_email='bnadlerjr@gmail.com',
    packages=['tavi', 'tavi.test'],
    scripts=[],
    url='http://pypi.python.org/pypi/Tavi/',
    license='LICENSE.txt',
    description='Super thin Object Document Mapper for MongoDB.',
    long_description=open('README').read(),
    install_requires=[
        "inflection >= 0.2.0",
        "pymongo >= 2.5.2"
    ]
)
