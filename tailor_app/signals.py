from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils import timezone
from .models import OrderTask, Order

@receiver(post_save, sender=OrderTask)
def check_order_completion(sender, instance, **kwargs):
    """
    After a task is saved, check if all tasks for its order are complete.
    If so, update the order's status to 'Completed'.
    """
    order = instance.order
    
    # Check if this was a task being marked as complete
    if instance.is_completed:
        # Check if there are any other tasks for this order that are NOT complete
        incomplete_tasks_exist = order.tasks.filter(is_completed=False).exists()
        
        if not incomplete_tasks_exist:
            # All tasks are complete, so update the order
            if order.status != 'Completed':
                order.status = 'Completed'
                order.save()
