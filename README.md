# Tavi

[![PyPI version](https://badge.fury.io/py/Tavi.png)](http://badge.fury.io/py/Tavi)
[![Build Status](https://travis-ci.org/bnadlerjr/tavi.png)](https://travis-ci.org/bnadlerjr/tavi)

Note: This is Alpha software. Refer to GitHub issues for a list of features that still need to be implemented.

Tavi (as in [Rikki Tikki Tavi](http://en.wikipedia.org/wiki/Rikki-Tikki-Tavi)) is an extremely thin Mongo object mapper for Python. It is a thin abstraction over [pymongo](http://api.mongodb.org/python/current/) that allows you to easily model your applications and persist your data in MongoDB.

## Getting Started

Install using pip:

    pip install Tavi

or clone the project and run:

    python setup.py install

Define your models:

```python
import tavi

class Product(tavi.documents.Document):
    name        = tavi.fields.StringField("name", required=True)
    sku         = tavi.fields.StringField("sku", required=True)
    description = tavi.fields.StringField("description", required=True)
    price       = tavi.fields.FloatField("price", min_value=0)
```

Use your models to create and find documents:

```python
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
```

For more details see [Using Tavi](#using-tavi).

### Dependencies

* pymongo >= 2.5.2
* inflection >= 0.2.0

## <a id="using-tavi"></a>Using Tavi

### Connecting to MongoDB
MongoDB connections are handled by the `tavi.Connection` class (which delegates to pymongo). Set up a connection like this:

```python
import tavi

tavi.Connection.setup("my_test_database", host="localhost", port=27017)
```

Alternatively, you can also use the MongoDB URI format:

```python
import tavi

tavi.Connection.setup("my_test_database", host="mongodb://localhost:27017/")
```

### Defining Documents

Documents are the building blocks for defining your models. An instantiated [```tavi.documents.Document```](#documents) class represents a single document in a MongoDB collection. It also provides a number of class methods used for querying the collection itself. You can embed documents inside other documents (rather than in their own collections) using the [```tavi.documents.EmbeddedDocument```](#embedded-documents) class.

### <a id="documents"></a>Documents

Document objects inherit from ```tavi.documents.Document```. You can [persist](#saving-documents) them to collections and they can contain embedded documents. They also come with support for [validations](#validations) and [querying](#finding-documents).

```python
import tavi

class Order(tavi.documents.Document):
    name     = tavi.fields.StringField("name", required=True)
    address  = tavi.fields.EmbeddedField("address", Address)
    email    = tavi.fields.StringField("email", required=True)
    pay_type = tavi.fields.StringField("pay_type", required=True, default="Mastercard")
```

Note: The collection name that is stored in Mongo is derived from the class name. In the example above, the collection in Mongo would be named `orders`. For the initial version of Tavi the collection name is not customizable. I have plans to support it in a future version, however.

Document objects are initialized like any other object. Additionally, they may be initialized with keyword arguments that set the field values.

```python
>>> order = Order(name="My Order", email="jdoe@example.com")

>>> order.name
"My Order"

>>> order.email
"jdoe@example.com"

>>> order.address
None

>>> order.pay_type
"Mastercard"
```

Any fields that are omitted from the list of keyword arguments are set to either `None` or their default value, if provided. Any keyword argument that is not a valid field is simply ignored.

Document objects have several attributes for retrieving information about them:

* `#bson_id` returns the ID of the document; this value can also be retrieved using `#_id`
* `#collection_name` returns the name of the collection
* `#data` returns a dictionary that contains all the fields and their values
* `#errors` returns a `tavi.errors.Errors` object (see [validations](#validations) for more info)
* `#fields` returns the list of fields defined for the document

#### (De-)Serialization

Document objects can be (de-)serialized from/to JSON. Under the hood it delegates to pymongo's [`bson.json_util`](http://api.mongodb.org/python/current/api/bson/json_util.html). The `#to_json` and `#from_json` methods convert to JSON and from JSON, respectively. In addition, the `#to_json` instance method can be given an optional array of fields to convert to JSON. By default, all fields are serialized.

```python
import tavi

class Order(tavi.documents.Document):
    name     = tavi.fields.StringField("name", required=True)
    address  = tavi.fields.EmbeddedField("address", Address)
    email    = tavi.fields.StringField("email", required=True)
    pay_type = tavi.fields.StringField("pay_type", required=True, default="Mastercard")
```

```python
>>> order = Order(name="My Order", email="jdoe@example.com", pay_type="Visa")

>>> order.to_json(["name", "email"])
... '{"name": "My Order", "email": "jdoe@example.com"}'
```

### <a id="embedded-documents"></a>Embedded Documents

Embedded documents are almost identical to Documents with one exception: they are saved inside of another document instead of in their own collection. They inherit from ```tavi.documents.EmbeddedDocument``` and have support for [validations](#validations).

```python
import tavi

class Address(tavi.documents.EmbeddedDocument):
    street      = tavi.fields.StringField("street")
    city        = tavi.fields.StringField("city")
    state       = tavi.fields.StringField("state")
    postal_code = tavi.fields.StringField("postal_code")
```

### Fields

Fields are how Tavi maps the attributes in your objects to attributes in the document for your collections in MongoDB. All fields inherit from ``tavi.base.fields.BaseField`` which provides some common [validations](#validations).

Fields are initialized with a name, which will be used when persisting the document to Mongo. This name can be different from the class's field name, for example:

```python
import tavi

class User(tavi.documents.Document):
    email  = tavi.fields.StringField("email")
    status = tavi.fields.StringField("my_status")
```

In the example above, you would refer to the class attribute `status`, but when the document is persisted `my_status` will be used as the name. This is useful if you have to support an existing Mongo database that has a different field name than the one you would like to use in your Python class.

#### <a id="basic-fields"></a>Basic Fields

There are several field types supported:

`tavi.fields.DateTimeField`:
Represents a naive datetime for a Mongo Document.

`tavi.fields.FloatField`:
Represents a floating point number for a Mongo Document. Supports the following additional validations:

* min_value: validates the minimum value the field value
* max_value: validates the maximum value the field value

`tavi.fields.IntegerField`:
Represents a integer number for a Mongo Document. Supports the following additional validations:

* min_value: validates the minimum value the field value
* max_value: validates the maximum value the field value

`tavi.fields.StringField`:
Represents a String field for a Mongo Document. Supports the following additional validations:

* length    : validates the field value has an exact length; default is `None`
* min_length: ensures field has a minimum number of characters; default is `None`
* max_length: ensures field is not more than a maximum number of characters; default is `None`
* pattern   : validates the field matches the given regular expression pattern; default is `None`

Note that leading and trailing whitespace is automatically stripped from StringField values.

#### <a id="custom-fields"></a>Custom Fields

If you need to add your own field types you may inherit from either ``tavi.base.fields.BaseField`` or one of the other field types. Any classes that inherit from ``tavi.base.fields.BaseField`` must implement the ``#validate`` method and call ``#super`` in order for validations to work. For example:

```python
    class MyCustomField(tavi.base.field.BaseField):
        def validate(self, instance, value):
            super(MyCustomField, self).validate(instance, value)
            # Your validation logic goes here...
```

#### Embedded Fields

`tavi.fields.EmbeddedField`'s are how embedded documents are placed in documents. For example, let's say we have defined an embedded document for an address.

```python
import tavi

class Address(tavi.documents.EmbeddedDocument):
    street      = tavi.fields.StringField("street")
    city        = tavi.fields.StringField("city")
    state       = tavi.fields.StringField("state")
    postal_code = tavi.fields.StringField("postal_code")
```

This embedded document can be placed into a user document using a `tavi.fields.EmbeddedField`.

```python
class User(tavi.documents.Document):
    name    = tavi.fields.StringField("name")
    address = tavi.fields.EmbeddedField("address", Address)
```

The address field can now be accessed through the user object...

```python
user = User()
user.address.street = "123 Elm Street"
user.address.city = "Anywhere"
user.address.state = "NY"
user.address.postal_code = "00000"
```

...and when the user is saved, the address is persisted along with it.

#### Embedded List Fields

`tavi.fields.ListFields` are used for embedding a list of Embedded fields. For example:

```python
import tavi

class OrderLine(tavi.documents.EmbeddedDocument):
    quantity    = tavi.fields.IntegerField("quantity")
    total_price = tavi.fields.FloatField("total_price")

class Order(Document):
    name        = tavi.fields.StringField("name")
    address     = tavi.fields.EmbeddedField("address", Address)
    email       = tavi.fields.StringField("email")
    pay_type    = tavi.fields.StringField("pay_type")
    order_lines = tavi.fields.ListField("order_lines")
```

In the above example, `OrderLine` is an `EmbeddedDocument` and `Order` is it's container `Document`. An `OrderLine` object can be appended to an `Order` like this:

```python
>>> order = Order(
...     name     = "John Doe",
...     email    = "jdoe@example.com",
...     pay_type = "Mastercard"
... )

>>> line_a = OrderLine(quantity=1, total_price=19.99)
>>> line_b = OrderLine(quantity=3, total_price=39.99)

>>> order.order_lines.append(line_a)
>>> order.order_lines.append(line_b)
```

When `order` is saved, it's `order_lines` are persisted as an array in the document.

```python
>>> order.order_lines[0].price
19.99
```

### <a id="validations"></a>Validations

Document objects support field validations through two attributes:

`#valid`: returns `True` or `False` indicating if all field validations are met
`#errors`: returns a `tavi.errors.Errors` object that holds information about all field errors

`tavi.errors.Errors` is a dictionary-like object with the following interface:

```python
import tavi

>>> errors = tavi.errors.Errors()

>>> errors.add("email", "is required")

>>> errors.get("email")
"is required"

>>> errors.full_messages_for("email")
"Email is required"

>>> errors.full_messages
["Email is required"]

>>> errors.count
1

>>> errors.clear

>>> errors.count
0
```

In practice, fields will handle adding and clearing errors themselves.

```python
import tavi

class User(tavi.documents.Document)
    email = StringField("email", required=True)
```

```python
>>> user = User()

>>> user.valid
False

>>> user.errors.get("email")
"is required"

>>> user.errors.full_messages_for("email")
"Email is required"

>>> user.errors.full_messages
["Email is required"]

>>> user.email = "jdoe@example.com"

>>> user.valid
True

>>> user.errors.count
0
```

Knowing how `tavi.errors.Errors` works is useful when you need to define your own [custom fields](#custom-fields).

#### Specifying Validations

All fields that inherit from `tavi.base.fields.BaseField` support the following validations:

required: indicates if the field is required; default is `False`

default: default value for the field; `None` if not given

choices: validates field value is a member of specified list

persist: boolean indicating if field should be persisted to Mongo; default is True

Here are some examples:

```python
import tavi

class User(tavi.documents.Document):
    email    = tavi.fields.StringField("email", required=True)
    age      = tavi.fields.IntegerField("age", default=0)
    pay_type = tavi.fields.StringField("pay_type", choices=["Mastercard", "Visa"])
    password = tavi.fields.StringField("password", persist=False)
```

Refer to [Basic Fields](#basic-fields) for a list of field types and their validations.

### Persistence

#### <a id="saving-documents"></a>Saving Documents

Document objects are persisted using the `#save` method. This method inserts the document into the collection if it does not exist or updates it if it does. The method returns `True` if the save was successful. Before performing the save, it ensures that the Document is valid and returns `False` if it was not.

If the document object has a field named `created_at`, this field's value will be set to the current time when the document is inserted. Also, if a field named `last_modified_at` is defined, this value will be set when the document is either inserted or updated.

#### <a id="finding-documents"></a>Finding Documents

Document objects can be retrieved using finder classmethods. There are two main finder methods: `#find` and `#find_one`. These are wrappers around the pymongo `#find` and `#find_one` methods and support all the same arguments. The difference is these methods wrap the return result into a Document object.

It is important to note that when using these methods, if you restrict the fields that are returned, the resulting document object(s) will have these fields set to `None`. If you later try to persist one of these objects, you will overwrite the value of the field. Therefore I recommend that you [use the collection directly](#using-pymongo) and have it return a dictionary result set.

Document objects also support two convenience finder methods: `#find_by_id` and `#find_all` which delegate to `#find_one` and `#find`, respectively.

You may also want to define your own custom finder methods. I recommend you delegate to the main finder methods like this:

```python
import tavi

class User(tavi.documents.Document):
    email     = tavi.fields.StringField("email")
    last_name = tavi.fields.StringField("last_name")

    @classmethod
    def find_by_email(cls, email)
        """Example custom finder."""
        return cls.find_one({"email": email})

    @classmethod
    def find_by_last_name(cls, last_name)
        """Example custom finder."""
        return cls.find({"last_name": last_name})
```

This way you will not have to wrap the results as document objects, since it will be done for you.

Document objects also support a `#count` method that will return the total number of documents in the collection.

#### Deleting Documents

Document objects may be removed from the collection using the `#delete` method.  There is no support for undoing this operation.

### Exceptions

Tavi defines several custom exceptions:

`TaviError`: Base error for all Tavi exceptions. If you need to define your own exceptions you may inherit from this class.

`TaviTypeError`: Raised when an operation or function is applied to an object of inappropriate type. For example, this error will be raised if you try to add an object that does not derive from `tavi.documents.EmbeddedDocument` to a `tavi.fields.EmbeddedField`.

`TaviConnectionError`: Raised when Tavi cannot connect to Mongo.

### <a id="using-pymongo"></a>Using pymongo

Tavi is just a thin wrapper for pymongo. When you need to work with pymongo directly, Tavi has a couple of convenience features to help you out.

Once a connection has been established, you can grab a handle to the database directly, like this:

```python
tavi.connection.Connection.database
```

The database object that is returned is a [pymongo database](http://api.mongodb.org/python/current/api/pymongo/database.html) and supports all of its methods.

You can access a collection directly from a document model. Given a document model:

```python
import tavi

class User(tavi.documents.Document):
    email =      tavi.fields.StringField("email")
    first_name = tavi.fields.StringField("first_name")
    last_name =  tavi.fields.StringField("last_name")
```

If you call

```python
User.collection
```

You will get back a handle to the `users` collection. This collection is a [pymongo collection](http://api.mongodb.org/python/current/api/pymongo/collection.html) and supports all of it's methods.

### Contributing

#### Environment Setup

Clone the repo, cd into folder then:

    virtualenv --no-site-packages env
    . env/bin/activate
    pip install -r requirements.txt

Run the tests using:

    python setup.py nosetests

Flake8 is used for tracking PEP8 compliance, cyclomatic complexity, etc. Run it using:

    flake8 tavi


#### Releasing a New Version

1. Increment version in setup.py
2. Update CHANGES.txt
3. Commit and tag version (ie. `git tag -a 1.4 -m 'Version 1.4'`)
4. Push tags (ie. `git push origin 1.4`)
5. Run `python setup.py sdist upload`

#### Issues / Roadmap

Use GitHub [issues](https://github.com/bnadlerjr/tavi/issues) for reporting bugs and feature requests. This library is meant to be lightweight so I probably won't be adding many features but feel free to submit pull requests for any critical features you think may be missing.

#### Patches / Pull Requests

* Fork the project.
* Make your feature addition or bug fix.
* Add tests for it. This is important so I don't break it in a future version unintentionally.
* Commit, do not mess with version or history (if you want to have your own version that is fine, but please bump version in a commit by itself I can ignore when I pull).
* Send me a pull request. Bonus points for topic branches.
