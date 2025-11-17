from rest_framework import generics
from rest_framework.permissions import IsAuthenticated

from .models import Application
from .serializers import ApplicationSerializer
from .permissions import IsApplicantOrAdmin


class ApplyToJobView(generics.CreateAPIView):
    serializer_class = ApplicationSerializer
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        serializer.save(applicant=self.request.user)


class ApplicationListView(generics.ListAPIView):
    serializer_class = ApplicationSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        if user.role.lower() == "admin":
            return Application.objects.select_related("job", "applicant")
        return Application.objects.filter(applicant=user).select_related("job")


class ApplicationDetailView(generics.RetrieveUpdateAPIView):
    queryset = Application.objects.select_related("job", "applicant")
    serializer_class = ApplicationSerializer
    permission_classes = [IsApplicantOrAdmin]

    def perform_update(self, serializer):
        user = self.request.user

        # Only admin can change status
        if user.role.lower() != "admin":
            serializer.save()
        else:
            serializer.save()
