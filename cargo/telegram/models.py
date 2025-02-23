from django.db import models
from clients.models import Client
# Create your models here.
# models.py
class NotificationTask(models.Model):
    message = models.TextField()
    status = models.CharField(max_length=20, choices=[
        ('pending', 'Pending'),
        ('success', 'Success'),
        ('failed', 'Failed')
    ])
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    error_message = models.TextField(blank=True, null=True)

    recipients = models.ManyToManyField('clients.Client', blank=True)

class NotificationImage(models.Model):
    task = models.ForeignKey(NotificationTask, on_delete=models.CASCADE, related_name='images')
    image = models.ImageField(upload_to='image/%Y/%m/%d/')
