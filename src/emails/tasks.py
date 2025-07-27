# yourapp/tasks.py
import django_rq


def update_email_cache():
    # This function will be called by the RQ worker
    print("Updating email cache...")
    # Add your logic to update the email cache here
    



def process_incoming_email(data):
    # do your processing here
    print("Processing email", data)
