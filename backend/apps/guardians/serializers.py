from rest_framework import serializers

from .models import Guardian


class GuardianSerializer(serializers.ModelSerializer):
    children_count = serializers.IntegerField(source="children.count", read_only=True)

    class Meta:
        model = Guardian
        fields = ("guardian_id", "name", "phone", "created_at", "children_count")
        read_only_fields = ("created_at", "children_count")
