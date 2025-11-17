from rest_framework.permissions import BasePermission


class IsApplicantOrAdmin(BasePermission):
    """
    Applicants can view their own applications.
    Admins can view all and update status.
    """

    def has_object_permission(self, request, view, obj):
        if request.user.role.lower() == "admin":
            return True
        return obj.applicant == request.user
