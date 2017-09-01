import collections
from types import MethodType

from django.db import models
from elasticsearch_dsl.field import (
    Attachment,
    Boolean,
    Byte,
    Completion,
    Date,
    Double,
    Field,
    Float,
    GeoPoint,
    GeoShape,
    Integer,
    Ip,
    Keyword,
    Long,
    Nested,
    Object,
    Short,
    Text,
)
from .exceptions import VariableLookupError


class LilyField(Field):
    def __init__(self, attr=None, **kwargs):
        super(LilyField, self).__init__(**kwargs)
        self._path = attr.split(".") if attr else []

    def __setattr__(self, key, value):
        if key == "get_value_from_instance":
            self.__dict__[key] = value
        else:
            super(LilyField, self).__setattr__(key, value)

    def get_value_from_instance(self, instance):
        """
        Given an model instance to index with ES, return the value that
        should be put into ES for this field.
        """
        if not instance:
            return None

        for attr in self._path:
            try:
                instance = instance[attr]
            except (
                TypeError, AttributeError,
                KeyError, ValueError, IndexError
            ):
                try:
                    instance = getattr(instance, attr)
                except (TypeError, AttributeError):
                    try:
                        instance = instance[int(attr)]
                    except (
                        IndexError,
                        ValueError,
                        KeyError,
                        TypeError
                    ):
                        raise VariableLookupError(
                            "Failed lookup for key [{}] in "
                            "{!r}".format(attr, instance)
                        )

            if (isinstance(instance, models.manager.Manager)):
                instance = instance.all()
            elif callable(instance):
                instance = instance()
            elif instance is None:
                return None

        return instance


class ObjectField(LilyField, Object):
    def _get_inner_field_data(self, obj):
        data = {}
        for name, field in self.properties.to_dict().items():
            if not isinstance(field, LilyField):
                continue

            if field._path == []:
                field._path = [name]

            data[name] = field.get_value_from_instance(obj)

        return data

    def get_value_from_instance(self, instance):
        objs = super(ObjectField, self).get_value_from_instance(instance)

        if objs is None:
            return {}
        if isinstance(objs, collections.Iterable):
            return [self._get_inner_field_data(obj) for obj in objs]

        return self._get_inner_field_data(objs)


def ListField(field):
    """
    This wraps a field so that when get_value_from_instance
    is called, the field's values are iterated over
    """
    original_get_value_from_instance = field.get_value_from_instance

    def get_value_from_instance(self, instance):
        return [value for value in original_get_value_from_instance(instance)]

    field.get_value_from_instance = MethodType(get_value_from_instance, field)
    return field


class AttachmentField(LilyField, Attachment):
    pass


class BooleanField(LilyField, Boolean):
    pass


class ByteField(LilyField, Byte):
    pass


class CompletionField(LilyField, Completion):
    pass


class DateField(LilyField, Date):
    pass


class DoubleField(LilyField, Double):
    pass


class FloatField(LilyField, Float):
    pass


class GeoPointField(LilyField, GeoPoint):
    pass


class GeoShapeField(LilyField, GeoShape):
    pass


class IntegerField(LilyField, Integer):
    pass


class IpField(LilyField, Ip):
    pass


class LongField(LilyField, Long):
    pass


class NestedField(Nested, ObjectField):
    pass


class ShortField(LilyField, Short):
    pass


class KeywordField(LilyField, Keyword):
    pass


class TextField(LilyField, Text):
    pass
