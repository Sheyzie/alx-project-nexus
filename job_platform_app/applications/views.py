from rest_framework import generics
from rest_framework.permissions import IsAuthenticated
from common.permissions import IsOwnerOrAdmin

from .models import Application
from .serializers import ApplicationSerializer
from .permissions import IsApplicantOrAdmin


class ApplyToJobView(generics.CreateAPIView):
    serializer_class = ApplicationSerializer
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        if self.request.user.is_admin or self.request.user.role.lower() == "admin":
            raise PermissionError("Admins cannot apply for jobs.")
        serializer.save(user=self.request.user)


class ApplicationListView(generics.ListAPIView):
    serializer_class = ApplicationSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        if self.request.user.is_admin or user.role.lower() == "admin":
            return Application.objects.select_related("job", "applicant")
        return Application.objects.filter(applicant=user).select_related("job")


class ApplicationDetailView(generics.RetrieveUpdateAPIView):
    queryset = Application.objects.select_related("job", "applicant")
    serializer_class = ApplicationSerializer
    permission_classes = [IsApplicantOrAdmin]

    def perform_update(self, serializer):
        user = self.request.user

        # Only admin can change status
        if not self.request.user.is_admin or user.role.lower() != "admin":
            if "status" in serializer.validated_data:
                raise PermissionError("You cannot change application status.")
        serializer.save()
