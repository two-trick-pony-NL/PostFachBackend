from django_elasticsearch_dsl import Document, fields
from django_elasticsearch_dsl.registries import registry
from users.models import Contact

@registry.register_document
class ContactDocument(Document):
    owner_id = fields.KeywordField()
    email_suggest = fields.CompletionField()

    class Index:
        name = 'contacts'
        settings = {
            'number_of_shards': 1,
            'number_of_replicas': 0
        }

    class Django:
        model = Contact
        fields = ['email', 'display_name']

    def prepare_owner_id(self, instance):
        return str(instance.owner_id)

    def prepare_email_suggest(self, instance):
        return {
            "input": [instance.email],
            "weight": 10
        }
