from django.db import models

class UserActive(models.Model):
    user = models.OneToOneField('auth.User', on_delete=models.CASCADE)
    is_active = models.BooleanField(default=False)
    code = models.CharField(max_length=6)

