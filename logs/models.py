from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save, pre_delete, pre_save
from django.dispatch import receiver
# Create your models here.


class Log(models.Model):
    users_involved = models.ManyToManyField(User, related_name='all_logs')
    created_by = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='logs_created')
    total = models.DecimalField(
        max_digits=10, decimal_places=2, null=False, default=0)
    settled = models.BooleanField(default=False)
    date_created = models.DateField(auto_now=True)
    log_hash = models.CharField(max_length=64, null=True)

    def __str__(self):
        return (f"{self.created_by.username} log {self.id}")


class Item(models.Model):
    log_id = models.ForeignKey(
        Log, on_delete=models.CASCADE, related_name='items')
    name = models.CharField(max_length=40)
    amount = models.DecimalField(max_digits=6, decimal_places=2)
    splitted_among = models.ManyToManyField(User, related_name='all_items')

    def __str__(self):
        return (f'{self.id} {self.name} of log {self.log_id}')


@receiver(post_save, sender=Item)
def item_created(sender, instance, created, **kwargs):
    log = Log.objects.get(pk=instance.log_id.id)
    log.total += instance.amount
    log.save()

# instance is the new instance going to be saved
# if new item is not being created, we subtract the old item's amount from total of log so after post_save the calculations are correct


@receiver(pre_save, sender=Item)
def item_updated(sender, instance, **kwargs):
    if not instance._state.adding:
        old_instance = Item.objects.get(pk=instance.pk)
        log = Log.objects.get(pk=instance.log_id.id)
        log.total -= old_instance.amount
        log.save()


@receiver(pre_delete, sender=Item)
def item_deleted(sender, instance, **kwargs):
    log = Log.objects.get(pk=instance.log_id.id)
    log.total -= instance.amount
    log.save()
