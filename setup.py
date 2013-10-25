# I prefer Markdown to reStructuredText. PyPi does not. This allows people to
# install and not get any errors.
try:
    import pypandoc
    long_description = pypandoc.convert('README.md', 'rst')
except (IOError, ImportError):
    long_description = (
        "Tavi (as in `Rikki Tikki Tavi "
        "<http://en.wikipedia.org/wiki/Rikki-Tikki-Tavi>`_) "
        "is an extremely thin Mongo object mapper for Python. It is a thin "
        "abstraction over `pymongo <http://api.mongodb.org/python/current/>`_ "
        "that allows you to easily model your applications and persist your "
        "data in MongoDB. See `README.md <http://github.com/bnadlerjr/tavi>`_ "
        "for more details."
    )

from setuptools import setup

setup(
    name='Tavi',
    version='0.0.1',
    author='Bob Nadler Jr.',
    author_email='bnadlerjr@gmail.com',
    packages=['tavi', 'tavi.test'],
    url='https://github.com/bnadlerjr/tavi',
    license='LICENSE.txt',
    description='Super thin Mongo object mapper for Python.',
    long_description=long_description,
    install_requires=[
        "inflection >= 0.2.0",
        "pymongo >= 2.5.2"
    ]
)
