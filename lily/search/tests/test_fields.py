from unittest import TestCase
from mock import Mock, NonCallableMock
from lily.search.fields import (
    LilyField,
    AttachmentField,
    BooleanField,
    ByteField,
    CompletionField,
    DateField,
    DoubleField,
    FloatField,
    GeoPointField,
    GeoShapeField,
    IntegerField,
    IpField,
    ListField,
    LongField,
    NestedField,
    ObjectField,
    ShortField,
    TextField, KeywordField)
from lily.search.exceptions import VariableLookupError


class LilyFieldTestCase(TestCase):
    def test_attr_to_path(self):
        field = LilyField(attr='field')
        self.assertEqual(field._path, ['field'])

        field = LilyField(attr='obj.field')
        self.assertEqual(field._path, ['obj', 'field'])

    def test_get_value_from_instance_attr(self):
        field = LilyField(attr='attr1')
        instance = NonCallableMock(attr1="foo", attr2="bar")
        self.assertEqual(field.get_value_from_instance(instance), "foo")

    def test_get_value_from_instance_related_attr(self):
        field = LilyField(attr='related.attr1')
        instance = NonCallableMock(attr1="foo",
                                   related=NonCallableMock(attr1="bar"))
        self.assertEqual(field.get_value_from_instance(instance), "bar")

    def test_get_value_from_instance_callable(self):
        field = LilyField(attr='callable')
        instance = NonCallableMock(callable=Mock(return_value="bar"))
        self.assertEqual(field.get_value_from_instance(instance), "bar")

    def test_get_value_from_instance_related_callable(self):
        field = LilyField(attr='related.callable')
        instance = NonCallableMock(related=NonCallableMock(
            callable=Mock(return_value="bar"), attr1="foo"))
        self.assertEqual(field.get_value_from_instance(instance), "bar")

    def test_get_value_from_instance_with_unknown_attr(self):
        class Dummy:
            attr1 = "foo"

        field = LilyField(attr='attr2')
        self.assertRaises(
            VariableLookupError, field.get_value_from_instance, Dummy()
        )

    def test_get_value_from_none(self):
        field = LilyField(attr='related.none')
        instance = NonCallableMock(attr1="foo", related=None)
        self.assertEqual(field.get_value_from_instance(instance), None)


class ObjectFieldTestCase(TestCase):
    def test_get_mapping(self):
        field = ObjectField(attr='person', properties={
            'first_name': TextField(analyzer='foo'),
            'last_name': TextField()
        })

        self.assertEqual({
            'type': 'object',
            'properties': {
                'first_name': {'type': 'text', 'analyzer': 'foo'},
                'last_name': {'type': 'text'},
            }
        }, field.to_dict())

    def test_get_value_from_instance(self):
        field = ObjectField(attr='person', properties={
            'first_name': TextField(analyzier='foo'),
            'last_name': TextField()
        })

        instance = NonCallableMock(person=NonCallableMock(
            first_name='foo', last_name='bar'))

        self.assertEqual(field.get_value_from_instance(instance), {
            'first_name': "foo",
            'last_name': "bar",
        })

    def test_get_value_from_instance_with_inner_objectfield(self):
        field = ObjectField(attr='person', properties={
            'first_name': TextField(analyzier='foo'),
            'last_name': TextField(),
            'aditional': ObjectField(properties={
                'age': IntegerField()
            })
        })

        instance = NonCallableMock(person=NonCallableMock(
            first_name="foo", last_name="bar",
            aditional=NonCallableMock(age=12)
        ))

        self.assertEqual(field.get_value_from_instance(instance), {
            'first_name': "foo",
            'last_name': "bar",
            'aditional': {'age': 12}
        })

    def test_get_value_from_instance_with_none_inner_objectfield(self):
        field = ObjectField(attr='person', properties={
            'first_name': TextField(analyzier='foo'),
            'last_name': TextField(),
            'aditional': ObjectField(properties={
                'age': IntegerField()
            })
        })

        instance = NonCallableMock(person=NonCallableMock(
            first_name="foo", last_name="bar",
            aditional=None
        ))

        self.assertEqual(field.get_value_from_instance(instance), {
            'first_name': "foo",
            'last_name': "bar",
            'aditional': {}
        })

    def test_get_value_from_iterable(self):
        field = ObjectField(attr='person', properties={
            'first_name': TextField(analyzier='foo'),
            'last_name': TextField()
        })

        instance = NonCallableMock(
            person=[
                NonCallableMock(
                    first_name="foo1", last_name="bar1"
                ),
                NonCallableMock(
                    first_name="foo2", last_name="bar2"
                )
            ]
        )

        self.assertEqual(field.get_value_from_instance(instance), [
            {
                'first_name': "foo1",
                'last_name': "bar1",
            },
            {
                'first_name': "foo2",
                'last_name': "bar2",
            }
        ])


class NestedFieldTestCase(TestCase):
    def test_get_mapping(self):
        field = NestedField(attr='person', properties={
            'first_name': TextField(analyzer='foo'),
            'last_name': TextField()
        })

        self.assertEqual({
            'type': 'nested',
            'properties': {
                'first_name': {'type': 'text', 'analyzer': 'foo'},
                'last_name': {'type': 'text'},
            }
        }, field.to_dict())


class BooleanFieldTestCase(TestCase):
    def test_get_mapping(self):
        field = BooleanField()

        self.assertEqual({
            'type': 'boolean',
        }, field.to_dict())


class DateFieldTestCase(TestCase):
    def test_get_mapping(self):
        field = DateField()

        self.assertEqual({
            'type': 'date',
        }, field.to_dict())


class TextFieldTestCase(TestCase):
    def test_get_mapping(self):
        field = TextField()

        self.assertEqual({
            'type': 'text',
        }, field.to_dict())


class CompletionFieldTestCase(TestCase):
    def test_get_mapping(self):
        field = CompletionField()

        self.assertEqual({
            'type': 'completion',
        }, field.to_dict())


class GeoPointFieldTestCase(TestCase):
    def test_get_mapping(self):
        field = GeoPointField()

        self.assertEqual({
            'type': 'geo_point',
        }, field.to_dict())


class GeoShapeFieldTestCase(TestCase):
    def test_get_mapping(self):
        field = GeoShapeField()

        self.assertEqual({
            'type': 'geo_shape'
        }, field.to_dict())


class ByteFieldTestCase(TestCase):
    def test_get_mapping(self):
        field = ByteField()

        self.assertEqual({
            'type': 'byte',
        }, field.to_dict())


class LongFieldTestCase(TestCase):
    def test_get_mapping(self):
        field = LongField()

        self.assertEqual({
            'type': 'long',
        }, field.to_dict())


class DoubleFieldTestCase(TestCase):
    def test_get_mapping(self):
        field = DoubleField()

        self.assertEqual({
            'type': 'double',
        }, field.to_dict())


class FloatFieldTestCase(TestCase):
    def test_get_mapping(self):
        field = FloatField()

        self.assertEqual({
            'type': 'float',
        }, field.to_dict())


class IpFieldTestCase(TestCase):
    def test_get_mapping(self):
        field = IpField()

        self.assertEqual({
            'type': 'ip',
        }, field.to_dict())


class ListFieldTestCase(TestCase):
    def test_get_mapping(self):
        field = ListField(TextField(attr='foo.bar'))
        self.assertEqual({
            'type': 'text',
        }, field.to_dict())

    def test_get_value_from_instance(self):
        instance = NonCallableMock(
            foo=NonCallableMock(bar=["alpha", "beta", "gamma"])
        )
        field = ListField(TextField(attr='foo.bar'))
        self.assertEqual(
            field.get_value_from_instance(instance), instance.foo.bar)


class AttachmentFieldTestCase(TestCase):
    def test_get_mapping(self):
        field = AttachmentField()

        self.assertEqual({
            'type': 'attachment',
        }, field.to_dict())


class ShortFieldTestCase(TestCase):
    def test_get_mapping(self):
        field = ShortField()

        self.assertEqual({
            'type': 'short',
        }, field.to_dict())


class KeywordFieldTestCase(TestCase):
    def test_get_mapping(self):
        field = KeywordField()

        self.assertEqual({
            'type': 'keyword',
        }, field.to_dict())
