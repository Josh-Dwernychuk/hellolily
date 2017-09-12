from lily.search.fields import BooleanField, IntegerField, KeywordField, TextField
from lily.search.indices import Index
from lily.search.search import DocType
from .models import LilyUser as LilyUserModel

user_index = Index('user')


@user_index.doc_type
class LilyUser(DocType):
    first_name = KeywordField()
    last_name = KeywordField()
    full_name = TextField()
    position = TextField()
    is_active = BooleanField()
    email = TextField()
    phone_number = TextField()
    internal_number = KeywordField()
    teams = IntegerField()
    tenant_id = IntegerField()

    def get_queryset(self):
        return LilyUserModel.objects.all()

    def prepare_teams(self, obj):
        return [team.id for team in obj.teams.all()]

    class Meta:
        model = LilyUserModel
