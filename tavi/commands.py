# -*- coding: utf-8 -*-
import collections
import datetime
import tavi.documents


class MongoCommand(object):
    def __init__(self, target, **kwargs):
        self.target = target
        self.kwargs = kwargs

    @property
    def name(self):
        raise "Not Implemented"

    def execute(self):
        self._now = datetime.datetime.utcnow()
        if hasattr(self.target, "last_modified_at"):
            self.old_last_modified_at = self.target.last_modified_at

        self._update_field("last_modified_at", self._now)

    def reset_fields(self):
        if hasattr(self.target, "last_modified_at"):
            self._update_field("last_modified_at", self.old_last_modified_at)

    def _update_field(self, name, timestamp):
        for field in self.target.fields:
            value = getattr(self.target, field)
            if name == field:
                setattr(self.target, name, timestamp)
            elif isinstance(value, collections.Iterable):
                for item in value:
                    if isinstance(item, tavi.documents.EmbeddedDocument):
                        setattr(item, name, timestamp)
            elif isinstance(value, tavi.documents.EmbeddedDocument):
                if hasattr(value, name):
                    setattr(value, name, timestamp)


class Insert(MongoCommand):
    @property
    def name(self):
        return "INSERT"

    def execute(self):
        super(Insert, self).execute()
        if hasattr(self.target, "created_at"):
            self.old_created_at = self.target.created_at

        self._update_field("created_at", self._now)

        collection = self.target.__class__.collection
        values = self.target.mongo_field_values
        self.target._id = collection.insert(values, **self.kwargs)

    def reset_fields(self):
        super(Insert, self).reset_fields()
        if hasattr(self.target, "created_at"):
            self._update_field("created_at", self.old_created_at)


class Update(MongoCommand):
    @property
    def name(self):
        return "UPDATE"

    def execute(self):
        super(Update, self).execute()
        self.kwargs["upsert"] = True
        self.target.__class__.collection.update(
            {"_id": self.target._id},
            {"$set": self.target.mongo_field_values},
            **self.kwargs)
