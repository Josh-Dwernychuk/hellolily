from elasticsearch_dsl import analyzer
from lily.search import fields
from lily.search.indices import Index
from lily.search.search import DocType

from .models import Car, Manufacturer, Ad


car_index = Index('test_cars')
car_index.settings(
    number_of_shards=1,
    number_of_replicas=0
)


html_strip = analyzer(
    'html_strip',
    tokenizer="standard",
    filter=["standard", "lowercase", "stop", "snowball"],
    char_filter=["html_strip"]
)


@car_index.doc_type
class CarDocument(DocType):
    manufacturer = fields.ObjectField(properties={
        'name': fields.TextField(),
        'country': fields.TextField(),
    })

    ads = fields.NestedField(properties={
        'description': fields.TextField(analyzer=html_strip),
        'title': fields.TextField(),
        'pk': fields.IntegerField(),
    })

    categories = fields.NestedField(properties={
        'title': fields.TextField(),
        'slug': fields.TextField(),
    })

    class Meta:
        model = Car
        fields = [
            'name',
            'launched',
            'type',
        ]

    def get_queryset(self):
        return super(CarDocument, self).get_queryset().select_related(
            'manufacturer')


@car_index.doc_type
class ManufacturerDocument(DocType):
    country = fields.TextField()

    class Meta:
        model = Manufacturer
        fields = [
            'name',
            'created',
            'country_code',
        ]


ad_index = Index('test_ads')
ad_index.settings(
    number_of_shards=1,
    number_of_replicas=0
)


@ad_index.doc_type
class AdDocument(DocType):
    description = fields.TextField(
        analyzer=html_strip,
        fields={'raw': fields.KeywordField()}
    )

    class Meta:
        model = Ad
        fields = [
            'title',
            'created',
            'modified',
            'url',
        ]
