from django.core.management.base import NoArgsCommand, CommandError
from datetime import datetime

from mturk_manager.models import TaskConfig, TaskItem
from mturk_manager.models import IN_PROGRESS
from mturk_manager.workflow import handle_reviewable_task

class Command(NoArgsCommand):
    help = "This cmd does nothing right meow"
    requires_model_validation = False

    def handle_noargs(self, **options):
        task_items = TaskItem.objects.filter(status=IN_PROGRESS)
        for task_item in task_items:
            handle_reviewable_task(task_item)
