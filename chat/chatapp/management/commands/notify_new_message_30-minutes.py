import json
import logging
import os
from datetime import datetime, timedelta
import time
from django.core.management.base import BaseCommand
from django.template.loader import get_template
from ...serializer import *
from ...models import *
from django.db.models import Q

class Command(BaseCommand):
    help = '30分間隔の受信チェック'
    def handle(self, *args, **options):
        for user in User.objects.filter(alert_freq = User.NOTIFY_ONCE_HALF_HOUR):
            # 自分が入っているルーム iteration
            for rm in user.rooms.all():
                if not rm.is_reading:
                    new_incomming_messages = ChatMessage.objects.filter(Q(room = rm.room) & ~Q(user = rm.user) & Q(sent_at__gt = rm.user.last_alerted) & Q(sent_at__gt = rm.last_logout))
                    if len(new_incomming_messages) > 0:
                        user.notify_new_message()
                        break
           
                
    

