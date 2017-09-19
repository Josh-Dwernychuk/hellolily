from unittest import TestCase
from mock import patch
from django.db import models
from lily.search.search import DocType
from lily.search import fields
from lily.search.exceptions import (ModelFieldNotMappedError)


class Car(models.Model):
    name = models.CharField(max_length=255)
    price = models.FloatField()
    not_indexed = models.TextField()
    manufacturer = models.ForeignKey('Manufacturer')

    class Meta:
        app_label = 'car'

    def type(self):
        return "break"


class Manufacturer(models.Model):
    name = models.CharField(max_length=255)

    class Meta:
        app_label = 'car'


class CarDocument(DocType):
    name = fields.TextField()
    price = fields.FloatField()
    color = fields.TextField()
    type = fields.TextField()

    def prepare_color(self, instance):
        return "blue"

    class Meta:
        model = Car
        index = 'car_index'
        related_models = [Manufacturer]


class DocTypeTestCase(TestCase):

    def test_model_class_added(self):
        self.assertEqual(CarDocument._doc_type.model, Car)

    def test_ignore_signal_default(self):
        self.assertFalse(CarDocument._doc_type.ignore_signals)

    def test_auto_refresh_default(self):
        self.assertTrue(CarDocument._doc_type.auto_refresh)

    def test_ignore_signal_added(self):
        class Car2Document(DocType):
            class Meta:
                model = Car
                ignore_signals = True
        self.assertTrue(Car2Document._doc_type.ignore_signals)

    def test_auto_refresh_added(self):
        class Car3Document(DocType):
            class Meta:
                model = Car
                auto_refresh = False
        self.assertFalse(Car3Document._doc_type.auto_refresh)

    def test_fields_populated(self):
        mapping = CarDocument._doc_type.mapping
        self.assertEqual(
            set(mapping.properties.properties.to_dict().keys()),
            set(['color', 'name', 'price', 'type'])
        )

    def test_related_models_added(self):
        related_models = CarDocument._doc_type.related_models
        self.assertEqual([Manufacturer], related_models)

    def test_to_field(self):
        doc = DocType()
        nameField = doc.to_field('name', Car._meta.get_field('name'))
        self.assertIsInstance(nameField, fields.TextField)
        self.assertEqual(nameField._path, ['name'])

    def test_to_field_with_unknown_field(self):
        doc = DocType()
        with self.assertRaises(ModelFieldNotMappedError):
            doc.to_field('manufacturer', Car._meta.get_field('manufacturer'))

    def test_mapping(self):
        self.assertEqual(
            CarDocument._doc_type.mapping.to_dict(), {
                'car_document': {
                    'properties': {
                        'name': {
                            'type': 'text'
                        },
                        'color': {
                            'type': 'text'
                        },
                        'type': {
                            'type': 'text'
                        },
                        'price': {
                            'type': 'float'
                        }
                    }
                }
            }
        )

    def test_get_queryset(self):
        qs = CarDocument().get_queryset()
        self.assertIsInstance(qs, models.QuerySet)
        self.assertEqual(qs.model, Car)

    def test_prepare(self):
        car = Car(name="Type 57", price=5400000.0, not_indexed="not_indexex")
        doc = CarDocument()
        prepared_data = doc.prepare(car)
        self.assertEqual(
            prepared_data, {
                'color': doc.prepare_color(None),
                'type': car.type(),
                'name': car.name,
                'price': car.price
            }
        )

    def test_model_instance_update(self):
        doc = CarDocument()
        car = Car(name="Type 57", price=5400000.0,
                  not_indexed="not_indexex", pk=51)
        with patch('lily.search.search.bulk') as mock:
            doc.update(car)
            actions = [{
                    '_id': car.pk,
                    '_op_type': 'index',
                    '_source': {
                        'name': car.name,
                        'price': car.price,
                        'type': car.type(),
                        'color': doc.prepare_color(None),
                    },
                    '_index': 'car_index',
                    '_type': 'car_document'
            }]
            self.assertEqual(1, mock.call_count)
            self.assertEqual(
                actions, list(mock.call_args_list[0][1]['actions'])
            )
            self.assertTrue(mock.call_args_list[0][1]['refresh'])
            self.assertEqual(
                doc.connection, mock.call_args_list[0][1]['client']
            )

    def test_model_instance_iterable_update(self):
        doc = CarDocument()
        car = Car(name="Type 57", price=5400000.0,
                  not_indexed="not_indexex", pk=51)
        car2 = Car(name="Type 42", price=50000.0,
                   not_indexed="not_indexex", pk=31)
        with patch('lily.search.search.bulk') as mock:
            doc.update([car, car2], action='update')
            actions = [{
                    '_id': car.pk,
                    '_op_type': 'update',
                    '_source': {
                        'name': car.name,
                        'price': car.price,
                        'type': car.type(),
                        'color': doc.prepare_color(None),
                    },
                    '_index': 'car_index',
                    '_type': 'car_document'
                },
                {
                    '_id': car2.pk,
                    '_op_type': 'update',
                    '_source': {
                        'name': car2.name,
                        'price': car2.price,
                        'type': car2.type(),
                        'color': doc.prepare_color(None),
                    },
                    '_index': 'car_index',
                    '_type': 'car_document'
            }]
            self.assertEqual(1, mock.call_count)
            self.assertEqual(
                actions, list(mock.call_args_list[0][1]['actions'])
            )
            self.assertTrue(mock.call_args_list[0][1]['refresh'])
            self.assertEqual(
                doc.connection, mock.call_args_list[0][1]['client']
            )

    def test_model_instance_update_no_refresh(self):
        doc = CarDocument()
        doc._doc_type.auto_refresh = False
        car = Car()
        with patch('lily.search.search.bulk') as mock:
            doc.update(car)
            self.assertNotIn('refresh', mock.call_args_list[0][1])
