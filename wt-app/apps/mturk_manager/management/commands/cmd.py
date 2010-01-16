from django.core.management.base import NoArgsCommand, CommandError
from datetime import datetime

from mturk_manager import HITConfig, HITItem

class Command(NoArgsCommand):
    help = "This cmd does nothing right meow"
    requires_model_validation = False

    def handle_noargs(self, **options):
        print 'what up dude'
