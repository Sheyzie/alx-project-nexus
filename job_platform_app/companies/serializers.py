from rest_framework import serializers

from .models import Company


class CompanySerializer(serializers.ModelSerializer):
    owner = serializers.ReadOnlyField(source="owner.id")

    class Meta:
        model = Company
        fields = "__all__"
        read_only_fields = ["id", "created_at", "owner"]
