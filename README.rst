Tavi
====

Tavi (as in `Rikki Tikki Tavi <http://en.wikipedia.org/wiki/Rikki-Tikki-Tavi>`)
is an extremely thin Object Document Mapper for MongoDB. It is a thin
abstraction over `pymongo <http://api.mongodb.org/python/current/>` that
simplifies boilerplate code and yet allows you to drop down to pymongo easily.

Quick Example
-------------

A sample model looks like this::
    from tavi import document, fields

    class Product(document.Document):
        name        = fields.StringField("name", required=True)
        sku         = fields.StringField("sku", required=True)
        description = fields.StringField("description", required=True)
        price       = fields.FloatField("price", min_value=0)

Using the above code, you can now manipulate your Product models in various
ways::

    >>> product = Product(name="Spam", sku="123", price=2.99)

    >>> product.valid
    False

    >>> product.errors.full_messages
    ['Description is required']

    >>> product.description = "A tasty canned precooked meat product."

    >>> product.valid
    True

    >>> product.save()
    True

    >>> for p in Product.find():
    ...     print p.name
    ...
    Spam

Getting Started
===============

Installation
------------

Dependencies
------------

Using Tavi
==========

Connecting to MongoDB
---------------------

Defining Document Objects
-------------------------

Defining Embedded Document Objects
----------------------------------

Fields
------

Basic Fields
^^^^^^^^^^^^

Embedded Fields
^^^^^^^^^^^^^^^

Embedded List Fields
^^^^^^^^^^^^^^^^^^^^

Validation
----------

Persistence
-----------

Saving Documents
^^^^^^^^^^^^^^^^

Finding Documents
^^^^^^^^^^^^^^^^^

Using pymongo
-------------
