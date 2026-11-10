from django.db import models
from django.contrib.auth.models import User


class Item(models.Model):

    CATEGORY_CHOICES = [
        ('Electronics', 'Electronics'),
        ('Documents', 'Documents'),
        ('Bags', 'Bags'),
        ('Clothing', 'Clothing'),
        ('Accessories', 'Accessories'),
        ('School Supplies', 'School Supplies'),
        ('Others', 'Others'),
    ]

    REPORT_TYPE_CHOICES = [
        ('Lost', 'Lost'),
        ('Found', 'Found'),
    ]

    STATUS_CHOICES = [
        ('Pending', 'Pending'),
        ('Approved', 'Approved'),
        ('Claimed', 'Claimed'),
        ('Returned', 'Returned'),
        ('Rejected', 'Rejected'),
    ]

    title = models.CharField(max_length=200)
    description = models.TextField()
    category = models.CharField(max_length=50, choices=CATEGORY_CHOICES)

    report_type = models.CharField(
        max_length=10,
        choices=REPORT_TYPE_CHOICES
    )

    location = models.CharField(max_length=200)
    date_lost_found = models.DateField()
    photo = models.ImageField(upload_to='items/', blank=True, null=True)

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='Pending'
    )

    reported_by = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='reported_items'
    )

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.report_type}: {self.title}"


class ClaimRequest(models.Model):

    STATUS_CHOICES = [
        ('Pending', 'Pending'),
        ('Approved', 'Approved'),
        ('Rejected', 'Rejected'),
    ]

    item = models.ForeignKey(
        Item,
        on_delete=models.CASCADE,
        related_name='claims'
    )

    claimant = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='claim_requests'
    )

    message = models.TextField(
        help_text='Explain why you believe this item belongs to you.'
    )

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='Pending'
    )

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['item', 'claimant'],
                name='unique_item_claimant'
            )
        ]

    def __str__(self):
        return f"{self.claimant.username} - {self.item.title}"


class Notification(models.Model):

    recipient = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='notifications'
    )

    message = models.CharField(max_length=255)

    is_read = models.BooleanField(default=False)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.recipient.username}: {self.message}"
