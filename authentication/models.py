from django.db import models
from django.contrib.auth.models import User
from django.core.validators import RegexValidator

class Chat(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    message = models.TextField()
    response = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['created_at']

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    phone_number = models.CharField(
        max_length=15,
        validators=[RegexValidator(r'^\+?1?\d{9,15}$', message="Enter a valid phone number.")],
        help_text="Phone number must be entered in the format: '+999999999'. Up to 15 digits allowed."
    )

    def __str__(self):
        return self.user.username
