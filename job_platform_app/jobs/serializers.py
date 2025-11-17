from rest_framework import serializers
from .models import Job, JobCategory


class JobCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = JobCategory
        fields = ["id", "name", "slug"]


class JobSerializer(serializers.ModelSerializer):
    category = JobCategorySerializer(read_only=True)
    category_id = serializers.PrimaryKeyRelatedField(
        source="category",
        queryset=JobCategory.objects.all(),
        write_only=True
    )

    class Meta:
        model = Job
        fields = [
            "id",
            "title",
            "description",
            "company",
            "location",
            "full_location",
            "latitude",
            "longitude",
            "job_type",
            "salary_min",
            "salary_max",
            "category",
            "category_id",
            "posted_by",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["posted_by", "latitude", "longitude"]
