from rest_framework import serializers

from .models import Child


class ChildSerializer(serializers.ModelSerializer):
    guardian_name = serializers.CharField(source="guardian.name", read_only=True)
    guardian_phone = serializers.CharField(source="guardian.phone", read_only=True)

    class Meta:
        model = Child
        fields = (
            "child_id",
            "name",
            "age",
            "guardian",
            "guardian_name",
            "guardian_phone",
            "created_at",
        )
        read_only_fields = ("created_at", "guardian_name", "guardian_phone")

    def validate_age(self, value):
        if value < 1 or value > 16:
            raise serializers.ValidationError("Child age must be between 1 and 16.")
        return value
