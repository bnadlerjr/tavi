# Tavi

Note: This is Alpha software. Refer to GitHub issues for a list of features that still need to be implemented.

Tavi (as in [Rikki Tikki Tavi](http://en.wikipedia.org/wiki/Rikki-Tikki-Tavi)) is an extremely thin Mongo object mapper for Python. It is a thin abstraction over [pymongo](http://api.mongodb.org/python/current/) that allows you to easily model your applications and persist your data in MongoDB.

## Getting Started

Install using pip:

    pip install Tavi

or clone the project and run:

    python setup.py install

Define your models:

```python
from tavi import document, fields

class Product(document.Document):
    name        = fields.StringField("name", required=True)
    sku         = fields.StringField("sku", required=True)
    description = fields.StringField("description", required=True)
    price       = fields.FloatField("price", min_value=0)
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

### Contributing

#### Issues / Roadmap

Use GitHub [issues](https://github.com/bnadlerjr/tavi/issues) for reporting bugs and feature requests. This library is meant to be lightweight so I probably won't be adding many features but feel free to submit pull requests for any critical features you think may be missing.

#### Patches / Pull Requests

* Fork the project.
* Make your feature addition or bug fix.
* Add tests for it. This is important so I don't break it in a future version unintentionally.
* Commit, do not mess with version or history (if you want to have your own version that is fine, but please bump version in a commit by itself I can ignore when I pull).
* Send me a pull request. Bonus points for topic branches.

## <a id="using-tavi"></a>Using Tavi

### Connecting to MongoDB
MongoDB connections are handled by the `tavi.connection.Connection` class (which delegates to pymongo). Set up a connection like this:

```python
tavi.connection.Connection.setup("my_test_database", host="localhost", port=27017)
```

Alternatively, you can also use the MongoDB URI format:

```python
tavi.connection.Connection.setup("my_test_database", host="mongodb://localhost:27017/")
```

### Defining Documents

Documents are the building blocks for defining your models. An instantiated [```tavi.document.Document```](#documents) class represents a single document in a MongoDB collection. It also provides a number of class methods used for querying the collection itself. You can embed documents inside other documents (rather than in their own collections) using the [```tavi.document.EmbeddedDocument```](#embedded-documents) class.

### <a id="documents"></a>Documents

Document objects inherit from ```tavi.document.Document```. You can [persist](#saving-documents) them to collections and they can contain embedded documents. They also come with support for [validations](#validations) and [querying](#finding-documents).

```python
class Order(tavi.document.Document):
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

### <a id="embedded-documents"></a>Embedded Documents

Embedded documents are almost identical to Documents with one exception: they are saved inside of another document instead of in their own collection. They inherit from ```tavi.document.EmbeddedDocument``` and have support for [validations](#validations).

```python
class Address(tavi.document.EmbeddedDocument):
    street      = tavi.fields.StringField("street")
    city        = tavi.fields.StringField("city")
    state       = tavi.fields.StringField("state")
    postal_code = tavi.fields.StringField("postal_code")
```

### Fields

Fields are how Tavi maps the attributes in your objects to attributes in the document for your collections in MongoDB. All fields inherit from ``tavi.base.field.BaseField`` which provides some common [validations](#validations).

#### Basic Fields

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

#### Custom Fields

If you need to add your own field types you may inherit from either ``tavi.base.field.BaseField`` or one of the other field types. Any classes that inherit from ``tavi.base.field.BaseField`` must implement the ``validate`` method and call ``super`` in order for validations to work. For example:

```python
    class MyCustomField(tavi.base.field.BaseField):
        def validate(self, instance, value):
            super(MyCustomField, self).validate(instance, value)
            # Your validation logic goes here...
```

#### Embedded Fields

`tavi.fields.EmbeddedField`'s are how embedded documents are placed in documents. For example, let's say we have defined an embedded document for an address.

```python
class Address(EmbeddedDocument):
    street      = StringField("street")
    city        = StringField("city")
    state       = StringField("state")
    postal_code = StringField("postal_code")
```

This embedded document can be placed into a user document using a `tavi.fields.EmbeddedField`.

```python
class User(Document):
    name = StringField("name")
    address = EmbeddedField("address", Address)
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

### <a id="validations"></a>Validations

### Persistence

#### <a id="saving-documents"></a>Saving Documents

#### <a id="finding-documents"></a>Finding Documents

### Exceptions

Tavi defines several custom exceptions:

`TaviError`: Base error for all Tavi exceptions. If you need to define your own exceptions you may inherit from this class.

`TaviTypeError`: Raised when an operation or function is applied to an object of inappropriate type. For example, this error will be raised if you try to add an object that does not derive from `tavi.documents.EmbeddedDocument` to a `tavi.fields.EmbeddedField`.

`TaviConnectionError`: Raised when Tavi cannot connect to Mongo.

### Using pymongo

Tavi is just a thin wrapper for pymongo. When you need to work with pymongo directly, Tavi has a couple of convenience features to help you out.

Once a connection has been established, you can grab a handle to the database directly, like this:

```python
tavi.connection.Connection.database
```

The database object that is returned is a [pymongo database](http://api.mongodb.org/python/current/api/pymongo/database.html) and supports all of its methods.

You can access a collection directly from a document model. Given a document model:

```python
class User(Document):
    email = StringField("email")
    first_name = StringField("first_name")
    last_name = StringField("last_name")
```

If you call

```python
User.collection
```

You will get back a handle to the `users` collection. This collection is a [pymongo collection](http://api.mongodb.org/python/current/api/pymongo/collection.html) and supports all of it's methods.
