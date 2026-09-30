from django.db import models

from apps.guardians.models import Guardian


class Child(models.Model):
    child_id = models.CharField(max_length=32, primary_key=True)
    name = models.CharField(max_length=120)
    age = models.PositiveSmallIntegerField()
    guardian = models.ForeignKey(
        Guardian, on_delete=models.PROTECT, related_name="children"
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["child_id"]
        indexes = [models.Index(fields=["name"]), models.Index(fields=["guardian"])]

    def __str__(self):
        return f"{self.child_id} - {self.name}"
