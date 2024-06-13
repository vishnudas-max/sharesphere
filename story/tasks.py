from celery import shared_task
from .models import Story

@shared_task
def delete_story(storyID):
    try:
        story = Story.objects.get(id=storyID)
        story.is_deleted = True
        story.save()
        return "Story deleted"
    except Story.DoesNotExist:
        return "Story not found"