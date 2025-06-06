from celery import shared_task

@shared_task
def test_task():
    print("✅ Celery Task Executed!")
    return "Task Done"

from celery import shared_task

@shared_task
def process_credit_application(application_id):
    # Yahan aap apna credit approval logic likh sakte hain
    print(f"Processing credit application ID: {application_id}")
    # For example, yahan database update ya email bhejna ho sakta hai
    return f"Application {application_id} processed"
