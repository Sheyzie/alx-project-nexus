from rest_framework import serializers

from .models import Application


class ApplicationSerializer(serializers.ModelSerializer):
    applicant = serializers.StringRelatedField(read_only=True)

    class Meta:
        model = Application
        fields = [
            "id",
            "job",
            "applicant",
            "resume",
            "cover_letter",
            "status",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["applicant", "status"]
