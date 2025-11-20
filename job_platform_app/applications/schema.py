import graphene
from graphene_django import DjangoObjectType
from django.shortcuts import get_object_or_404
from jobs.models import Job

from .models import Application

class ApplicationType(DjangoObjectType):
    class Meta:
        model = Application
        fields = (
            "id",
            "job",
            "applicant",
            "resume",
            "cover_letter",
            "status",
            "created_at",
        )


class ApplicationQuery(graphene.ObjectType):
    applications = graphene.List(ApplicationType)
    application = graphene.Field(ApplicationType, id=graphene.UUID(required=True))

    def resolve_applications(root, info):
        user = info.context.user
        if user.is_anonymous:
            raise Exception("User not logged in!")
        return Application.objects.select_related("job", "applicant").all()

    def resolve_application(root, info, id):
        user = info.context.user
        if user.is_anonymous:
            raise Exception("User not logged in!")
        return Application.objects.get(pk=id)
    

class ApplyForJob(graphene.Mutation):
    class Arguments:
        job_id = graphene.UUID(required=True)
        resume = graphene.String(required=True)
        cover_letter = graphene.String()

    application = graphene.Field(lambda: ApplicationType)

    def mutate(self, info, job_id, resume, cover_letter=""):
        user = info.context.user
        if user.is_anonymous or user.role.lower() != 'user':
            raise Exception("Unauthorised. Only a user can apply!")
        
        job = get_object_or_404(Job, pk=job_id)

        application = Application.objects.create(
            job=job,
            applicant=user,
            resume=resume,
            cover_letter=cover_letter
        )

        return ApplyForJob(application=application)


class UpdateApplicationStatus(graphene.Mutation):
    class Arguments:
        id = graphene.UUID(required=True)
        status = graphene.String(required=True)

    application = graphene.Field(ApplicationType)

    def mutate(self, info, id, status):
        user = info.context.user
        if user.is_anonymous or user.role.lower() != 'admin':
            raise Exception("Unauthorised. Only a admin can update!")
        
        application = get_object_or_404(Application, pk=id)

        application.status = status
        application.save()

        return UpdateApplicationStatus(application=application)



