from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone

class UserToken(models.Model):
    """Model for tracking refresh tokens"""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='auth_tokens')
    refresh_token = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField()
    is_active = models.BooleanField(default=True)

    def is_valid(self):
        """Check if token is still valid"""
        return self.is_active and self.expires_at > timezone.now()

    def revoke(self):
        """Revoke this token"""
        self.is_active = False
        self.save()

    class Meta:
        db_table = 'user_tokens'
        verbose_name = 'User Token'
        verbose_name_plural = 'User Tokens'
