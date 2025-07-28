from users.documents.contacts import ContactDocument
from emails.documents.email import EmailDocument


def search_contacts(query: str, user_id):
    s = ContactDocument.search().query("multi_match", query=query, fields=[
        "email", "display_name"
    ])
    s = s.filter("term", owner_id=user_id)
    return s[:10].execute()


def search_emails(query: str, user_id):
    s = EmailDocument.search().query("multi_match", query=query, fields=[
        "subject", "body", "html_body", "from_email"
    ])
    s = s.filter("term", owner_id=user_id)
    return s[:10].execute()

def autocomplete_contacts(partial: str, user_id):
    s = ContactDocument.search()
    s = s.suggest(
        'email_suggestions',
        partial,
        completion={
            "field": "email_suggest",
            "fuzzy": {
                "fuzziness": 1
            }
        }
    )
    s = s.filter("term", owner_id=user_id)
    response = s.execute()
    options = response.suggest.email_suggestions[0].options
    return [opt._source.email for opt in options]
