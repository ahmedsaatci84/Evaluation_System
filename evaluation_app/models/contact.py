from django.db import models


class ContactMessage(models.Model):
    name = models.CharField(max_length=100)
    email = models.EmailField()
    phone = models.CharField(max_length=20, blank=True, null=True)
    subject = models.CharField(max_length=200)
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    is_read = models.BooleanField(default=False)

    class Meta:
        managed = True
        db_table = 'contact_messages'
        verbose_name = 'Contact Message'
        verbose_name_plural = 'Contact Messages'
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.name} - {self.subject} ({self.created_at.strftime('%Y-%m-%d')})"

    def mark_as_read(self):
        self.is_read = True
        self.save(update_fields=['is_read'])

    def mark_as_unread(self):
        self.is_read = False
        self.save(update_fields=['is_read'])

    def get_status_display(self):
        return "Read" if self.is_read else "Unread"

    @classmethod
    def get_unread_count(cls):
        return cls.objects.filter(is_read=False).count()

    @classmethod
    def get_recent_messages(cls, limit=5):
        return cls.objects.all()[:limit]
