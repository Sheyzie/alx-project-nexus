from rest_framework import generics, filters
from common.permissions import IsAdminOrReadOnly

from .models import Job, JobCategory
from .serializers import JobSerializer, JobCategorySerializer
# from .permissions import IsAdminOrReadOnly


class JobCategoryListCreateView(generics.ListCreateAPIView):
    queryset = JobCategory.objects.all()
    serializer_class = JobCategorySerializer
    permission_classes = [IsAdminOrReadOnly]


class JobCategoryDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = JobCategory.objects.all()
    serializer_class = JobCategorySerializer
    permission_classes = [IsAdminOrReadOnly]


class JobListCreateView(generics.ListCreateAPIView):
    serializer_class = JobSerializer
    permission_classes = [IsAdminOrReadOnly]

    # DRF native search
    filter_backends = [filters.SearchFilter]
    search_fields = ["title", "company"]

    def get_queryset(self):
        queryset = Job.objects.select_related("category", "posted_by")

        # Manual filters
        job_type = self.request.query_params.get("job_type")
        category = self.request.query_params.get("category")

        if job_type:
            queryset = queryset.filter(job_type=job_type)

        if category:
            queryset = queryset.filter(category_id=category)

        return queryset

    def perform_create(self, serializer):
        serializer.save(posted_by=self.request.user)


class JobDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Job.objects.select_related("category", "posted_by")
    serializer_class = JobSerializer
    permission_classes = [IsAdminOrReadOnly]
