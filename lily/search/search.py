from __future__ import unicode_literals

from django.db import models
from django.utils.six import add_metaclass, iteritems
from elasticsearch.helpers import bulk
from elasticsearch_dsl import DocType as DSLDocType
from elasticsearch_dsl.document import DocTypeMeta as DSLDocTypeMeta

from .exceptions import ModelFieldNotMappedError
from .fields import (
    BooleanField,
    DateField,
    LilyField,
    DoubleField,
    IntegerField,
    LongField,
    ShortField,
    TextField,
)

model_field_class_to_field_class = {
    models.AutoField: IntegerField,
    models.BigIntegerField: LongField,
    models.BooleanField: BooleanField,
    models.CharField: TextField,
    models.DateField: DateField,
    models.DateTimeField: DateField,
    models.EmailField: TextField,
    models.FileField: TextField,
    models.FilePathField: TextField,
    models.FloatField: DoubleField,
    models.ImageField: TextField,
    models.IntegerField: IntegerField,
    models.NullBooleanField: BooleanField,
    models.PositiveIntegerField: IntegerField,
    models.PositiveSmallIntegerField: ShortField,
    models.SlugField: TextField,
    models.SmallIntegerField: ShortField,
    models.TextField: TextField,
    models.TimeField: LongField,
    models.URLField: TextField,
}


class DocTypeMeta(DSLDocTypeMeta):
    def __new__(cls, name, bases, attrs):
        """
        Subclass default DocTypeMeta to generate ES fields from django
        models fields
        """
        super_new = super(DocTypeMeta, cls).__new__

        parents = [b for b in bases if isinstance(b, DocTypeMeta)]
        if not parents:
            return super_new(cls, name, bases, attrs)

        model = attrs['Meta'].model

        ignore_signals = getattr(attrs['Meta'], "ignore_signals", False)
        auto_refresh = getattr(attrs['Meta'], 'auto_refresh', True)
        related_models = getattr(attrs['Meta'], "related_models", [])

        cls = super_new(cls, name, bases, attrs)

        cls._doc_type.model = model
        cls._doc_type.ignore_signals = ignore_signals
        cls._doc_type.auto_refresh = auto_refresh
        cls._doc_type.related_models = related_models
        cls._doc_type._fields = (lambda: cls._doc_type.mapping.properties.properties.to_dict())

        return cls


@add_metaclass(DocTypeMeta)
class DocType(DSLDocType):
    def __eq__(self, other):
        return id(self) == id(other)

    def __hash__(self):
        return id(self)

    def get_queryset(self):
        """
        Return the queryset that should be indexed by this doc type.
        """
        return self._doc_type.model._default_manager.all()

    def prepare(self, instance):
        """
        Take a model instance, and turn it into a dict that can be serialized
        based on the fields defined on this DocType subclass
        """
        data = {}
        for name, field in iteritems(self._doc_type._fields()):
            if not isinstance(field, LilyField):
                continue

            if field._path == []:
                field._path = [name]

            prep_func = getattr(
                self,
                "prepare_" + name,
                field.get_value_from_instance
            )
            data[name] = prep_func(instance)

        return data

    def to_field(self, field_name, model_field):
        """
        Returns the elasticsearch field instance appropriate for the model
        field class. This is a good place to hook into if you have more complex
        model field to ES field logic
        """
        try:
            return model_field_class_to_field_class[
                model_field.__class__](attr=field_name)
        except KeyError:
            raise ModelFieldNotMappedError(
                "Cannot convert model field {} "
                "to an Elasticsearch field!".format(field_name)
            )

    def bulk(self, actions, **kwargs):
        return bulk(client=self.connection, actions=actions, **kwargs)

    def update(self, thing, refresh=None, action='index', **kwargs):
        """
        Update each document in ES for a model, iterable of models or queryset
        """
        if refresh is True or (
            refresh is None and self._doc_type.auto_refresh
        ):
            kwargs['refresh'] = True

        if isinstance(thing, models.Model):
            thing = [thing]

        actions = ({
            '_op_type': action,
            '_index': str(self._doc_type.index),
            '_type': self._doc_type.mapping.doc_type,
            '_id': model.pk,
            '_source': self.prepare(model) if action != 'delete' else None,
        } for model in thing)

        return self.bulk(actions, **kwargs)
