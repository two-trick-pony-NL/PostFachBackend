from django_elasticsearch_dsl import Document, fields
from django_elasticsearch_dsl.registries import registry
from emails.models import Email

@registry.register_document
class EmailDocument(Document):
    owner_id = fields.KeywordField()
    from_email = fields.TextField()
    subject = fields.TextField()
    body = fields.TextField()
    html_body = fields.TextField()

    class Index:
        name = 'emails'
        settings = {
            'number_of_shards': 1,
            'number_of_replicas': 0
        }

    class Django:
        model = Email
        fields = [
            'status',
            'direction',
            'is_read',
            'is_starred',
            'is_archived',
            'is_snoozed',
            'is_pinned',
            'is_replied',
            'is_draft',
            'received_at',
        ]

    def prepare_owner_id(self, instance):
        return str(instance.owner_id)
