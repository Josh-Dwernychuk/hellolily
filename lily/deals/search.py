from lily.accounts.models import Account
from lily.search.base_mapping import BaseMapping
from lily.search.fields import ObjectField, IntegerField, TextField, FloatField, BooleanField, DateField, KeywordField
from lily.search.indices import Index
from lily.search.search import DocType
from lily.tags.models import Tag

from .models import Deal as DealModel

index = Index('deal')


class DealMapping(BaseMapping):
    @classmethod
    def get_model(cls):
        return DealModel

    @classmethod
    def get_mapping(cls):
        """
        Returns an Elasticsearch mapping for this MappingType.
        """
        mapping = super(DealMapping, cls).get_mapping()
        mapping['properties'].update({
            'account': {
                'type': 'object',
                'properties': {
                    'id': {'type': 'integer'},
                    'customer_id': {
                        'type': 'string',
                        'index_analyzer': 'normal_edge_analyzer'
                    },
                    'name': {
                        'type': 'string',
                        'index_analyzer': 'normal_edge_analyzer',
                    },
                    'is_deleted': {'type': 'boolean'},
                }
            },
            'amount_once': {
                'type': 'float',
            },
            'amount_recurring': {
                'type': 'float',
            },
            'assigned_to': {
                'type': 'object',
                'properties': {
                    'id': {'type': 'integer'},
                    'full_name': {
                        'type': 'string',
                        'analyzer': 'normal_edge_analyzer',
                    },
                },
            },
            'assigned_to_teams': {
                'type': 'integer',
            },
            'card_sent': {
                'type': 'boolean',
            },
            'closed_date': {
                'type': 'date',
            },
            'contact': {
                'type': 'object',
                'properties': {
                    'id': {'type': 'integer'},
                    'full_name': {
                        'type': 'string',
                        'analyzer': 'normal_edge_analyzer',
                    },
                    'is_deleted': {'type': 'boolean'},
                },
            },
            'contacted_by': {
                'type': 'object',
                'properties': {
                    'id': {'type': 'integer'},
                    'full_name': {
                        'type': 'string',
                        'analyzer': 'normal_edge_analyzer',
                    },
                },
            },
            'created': {
                'type': 'date',
            },
            'created_by': {
                'type': 'object',
                'properties': {
                    'id': {'type': 'integer'},
                    'full_name': {
                        'type': 'string',
                        'analyzer': 'normal_edge_analyzer',
                    },
                },
            },
            'currency': {
                'type': 'string',
            },
            'currency_display': {
                'type': 'string',
            },
            'description': {
                'type': 'string',
                'index_analyzer': 'normal_edge_analyzer',
            },
            'found_through': {
                'type': 'object',
                'properties': {
                    'id': {'type': 'integer'},
                    'name': {
                        'type': 'string',
                        'analyzer': 'normal_edge_analyzer',
                    },
                },
            },
            'is_archived': {
                'type': 'boolean',
            },
            'is_checked': {
                'type': 'boolean',
            },
            'modified': {
                'type': 'date',
            },
            'name': {
                'type': 'string',
                'index_analyzer': 'normal_ngram_analyzer',
            },
            'new_business': {
                'type': 'boolean',
            },
            'newly_assigned': {
                'type': 'boolean',
            },
            'next_step': {
                'type': 'object',
                'properties': {
                    'id': {'type': 'integer'},
                    'name': {
                        'type': 'string',
                        'analyzer': 'normal_edge_analyzer',
                    },
                    'date_increment': {'type': 'integer'},
                    'position': {'type': 'integer'}
                }
            },
            'next_step_date': {
                'type': 'date',
            },
            'quote_id': {
                'type': 'string'
            },
            'status': {
                'type': 'object',
                'properties': {
                    'id': {'type': 'integer'},
                    'name': {
                        'type': 'string',
                        'analyzer': 'normal_edge_analyzer',
                    },
                    'position': {'type': 'integer'},
                },
            },
            'tags': {
                'type': 'object',
                'properties': {
                    'id': {'type': 'integer'},
                    'name': {
                        'type': 'string',
                        'index_analyzer': 'normal_edge_analyzer',
                    },
                    'object_id': {'type': 'integer'},
                },
            },
            'twitter_checked': {
                'type': 'boolean',
            },
            'why_customer': {
                'type': 'object',
                'properties': {
                    'id': {'type': 'integer'},
                    'name': {
                        'type': 'string',
                        'analyzer': 'normal_edge_analyzer',
                    },
                },
            },
            'why_lost': {
                'type': 'string',
                'index_analyzer': 'normal_edge_analyzer',
            }
        })
        return mapping

    @classmethod
    def get_related_models(cls):
        """
        Maps related models, how to get an instance list from a signal sender.
        """
        return {
            Account: lambda obj: obj.deal_set.all(),
            Tag: lambda obj: [obj.subject],
        }

    @classmethod
    def prepare_batch(cls, queryset):
        """
        Optimize a queryset for batch indexing.
        """
        return queryset.prefetch_related(
            'account',
            'assigned_to',
            'tags',
        )

    @classmethod
    def obj_to_doc(cls, obj):
        """
        Translate an object to an index document.
        """
        return {
            'account': {
                'id': obj.account.id,
                'name': obj.account.name,
                'customer_id': obj.account.customer_id,
                'is_deleted': obj.account.is_deleted,
            } if obj.account else None,
            'amount_once': obj.amount_once,
            'amount_recurring': obj.amount_recurring,
            'assigned_to': {
                'id': obj.assigned_to.id,
                'full_name': obj.assigned_to.full_name,
            } if obj.assigned_to else None,
            'assigned_to_teams': [team.id for team in obj.assigned_to_teams.all()],
            'card_sent': obj.card_sent,
            'closed_date': obj.closed_date,
            'contact': {
                'id': obj.contact.id,
                'full_name': obj.contact.full_name,
                'is_deleted': obj.contact.is_deleted,
            } if obj.contact else None,
            'contacted_by': {
                'id': obj.contacted_by.id,
                'name': obj.contacted_by.name,
            } if obj.contacted_by else None,
            'content_type': obj.content_type.id,
            'created': obj.created,
            'created_by': {
                'id': obj.created_by.id,
                'full_name': obj.created_by.full_name,
            } if obj.created_by else None,
            'currency': obj.currency,
            'currency_display': obj.get_currency_display(),
            'description': obj.description,
            'found_through': {
                'id': obj.found_through.id,
                'name': obj.found_through.name,
            } if obj.found_through else None,
            'is_archived': obj.is_archived,
            'is_checked': obj.is_checked,
            'modified': obj.modified,
            'name': obj.name,
            'new_business': obj.new_business,
            'next_step': {
                'id': obj.next_step.id,
                'name': obj.next_step.name,
                'date_increment': obj.next_step.date_increment,
                'position': obj.next_step.position,
            } if obj.next_step else None,
            'newly_assigned': obj.newly_assigned,
            'next_step_date': obj.next_step_date,
            'quote_id': obj.quote_id,
            'status': {
                'id': obj.status.id,
                'name': obj.status.name,
                'position': obj.status.position,
            },
            'tags': [{
                'id': tag.id,
                'name': tag.name,
                'object_id': tag.object_id,
            } for tag in obj.tags.all()],
            'twitter_checked': obj.twitter_checked,
            'why_customer': {
                'id': obj.why_customer.id,
                'name': obj.why_customer.name,
            } if obj.why_customer else None,
            'why_lost': obj.why_lost.name if obj.why_lost else None,
        }


@index.doc_type
class Deal(DocType):
    account = ObjectField(properties={
        'id': IntegerField(),
        'customer_id': TextField(),
        'name': TextField(),
        'is_deleted': BooleanField(),
    })
    amount_once = FloatField(fields={
        'sortable': FloatField(),
    })
    amount_recurring = FloatField(fields={
        'sortable': FloatField(),
    })
    assigned_to = ObjectField(properties={
        'id': IntegerField(),
        'full_name': TextField(fields={'sortable': KeywordField()}),
    })
    assigned_to_teams = IntegerField()
    card_sent = BooleanField()
    closed_date = DateField()
    contact = ObjectField(properties={
        'id': IntegerField(),
        'full_name': TextField(),
        'is_deleted': BooleanField(),
    })
    contacted_by = ObjectField(properties={
        'id': IntegerField(),
        'full_name': TextField(),
    })
    created = DateField(fields={'sortable': DateField()})
    created_by = ObjectField(properties={
        'id': IntegerField(),
        'full_name': TextField(fields={'sortable': KeywordField()}),
    })
    currency = KeywordField()
    currency_display = KeywordField()
    description = TextField()
    found_through = ObjectField(properties={
        'id': IntegerField(),
        'name': TextField(),
    })
    is_archived = BooleanField()
    is_checked = BooleanField()
    is_deleted = BooleanField()
    modified = DateField()
    name = TextField()
    new_business = BooleanField(fields={'sortable': BooleanField()})
    newly_assigned = BooleanField()
    next_step = ObjectField(properties={
        'id': IntegerField(),
        'name': TextField(fields={'sortable': KeywordField()}),
        'date_increment': IntegerField(),
        'position': IntegerField(),
    })
    next_step_date = DateField(fields={
        'sortable': DateField()
    })
    quote_id = KeywordField()
    status = ObjectField(properties={
        'id': IntegerField(),
        'name': TextField(fields={'sortable': KeywordField()}),
        'position': IntegerField(),
    })
    tags = ObjectField(properties={
        'id': IntegerField(),
        'name': TextField(),
        'object_id': IntegerField(),
    })
    tenant_id = IntegerField()
    twitter_checked = BooleanField()
    why_customer = ObjectField(properties={
        'id': IntegerField(),
        'name': TextField(),
    })
    why_lost = TextField()

    def get_queryset(self):
        return DealModel.objects.all()

    def prepare_account(self, obj):
        return {
            'id': obj.account.id,
            'name': obj.account.name,
            'customer_id': obj.account.customer_id,
            'is_deleted': obj.account.is_deleted,
        } if obj.account else None

    def prepare_assigned_to(self, obj):
        return {
            'id': obj.assigned_to.id,
            'full_name': obj.assigned_to.full_name,
        } if obj.assigned_to else None

    def prepare_assigned_to_teams(self, obj):
        return [team.id for team in obj.assigned_to_teams.all()]

    def prepare_contact(self, obj):
        return {
            'id': obj.contact.id,
            'full_name': obj.contact.full_name,
            'is_deleted': obj.contact.is_deleted,
        } if obj.contact else None

    def prepare_contacted_by(self, obj):
        return {
            'id': obj.contacted_by.id,
            'name': obj.contacted_by.name,
        } if obj.contacted_by else None

    def prepare_content_type(self, obj):
        return obj.content_type.id

    def prepare_created_by(self, obj):
        return {
            'id': obj.created_by.id,
            'full_name': obj.created_by.full_name,
        } if obj.created_by else None

    def prepare_currency_display(self, obj):
        return obj.get_currency_display()

    def prepare_found_through(self, obj):
        return {
            'id': obj.found_through.id,
            'name': obj.found_through.name,
        } if obj.found_through else None

    def prepare_is_deleted(self, obj):
        return obj.is_deleted

    def prepare_next_step(self, obj):
        return {
            'id': obj.next_step.id,
            'name': obj.next_step.name,
            'date_increment': obj.next_step.date_increment,
            'position': obj.next_step.position,
        } if obj.next_step else None

    def prepare_tags(self, obj):
        return [{
            'id': tag.id,
            'name': tag.name,
            'object_id': tag.object_id,
        } for tag in obj.tags.all()]

    def prepare_why_customer(self, obj):
        return {
            'id': obj.why_customer.id,
            'name': obj.why_customer.name,
        } if obj.why_customer else None

    def prepare_why_lost(self, obj):
        return obj.why_lost.name if obj.why_lost else None

    class Meta:
        model = DealModel
