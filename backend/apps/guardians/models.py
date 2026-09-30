from django.db import models


class Guardian(models.Model):
    guardian_id = models.CharField(max_length=32, primary_key=True)
    name = models.CharField(max_length=120)
    phone = models.CharField(max_length=20)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["guardian_id"]
        indexes = [models.Index(fields=["name"])]

    def __str__(self):
        return f"{self.guardian_id} - {self.name}"
