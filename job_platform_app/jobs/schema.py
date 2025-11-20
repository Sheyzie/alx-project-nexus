import graphene
from graphene_django import DjangoObjectType
from django.shortcuts import get_object_or_404
from django.contrib.auth import get_user_model

from .models import Job, JobCategory


User = get_user_model()


class CategoryType(DjangoObjectType):
    class Meta:
        model = JobCategory
        fields = ("id", "name", "slug")

class JobType(DjangoObjectType):
    class Meta:
        model = Job
        fields = (
            "id",
            "title",
            "description",
            "company",
            "job_type",
            "location",
            "latitude",
            "longitude",
            "salary_min",
            "salary_max",
            "category",
            "posted_by",
            "created_at",
        )


class JobQuery(graphene.ObjectType):
    jobs = graphene.List(JobType)
    job = graphene.Field(JobType, id=graphene.UUID(required=True))

    categories = graphene.List(CategoryType)
    category = graphene.Field(CategoryType, id=graphene.UUID(required=True))

    def resolve_jobs(root, info):
        user = info.context.user
        if user.is_anonymous:
            raise Exception("User not logged in!")
        return Job.objects.all()

    def resolve_job(root, info, id):
        user = info.context.user
        if user.is_anonymous:
            raise Exception("User not logged in!")
        return Job.objects.get(pk=id)

    def resolve_categories(root, info):
        user = info.context.user
        if user.is_anonymous:
            raise Exception("User not logged in!")
        return JobCategory.objects.all()

    def resolve_category(root, info, id):
        user = info.context.user
        if user.is_anonymous:
            raise Exception("User not logged in!")
        return JobCategory.objects.get(pk=id)
    

# -------------------------------
# Input Types
# -------------------------------    

class JobInput(graphene.InputObjectType):
    title = graphene.String(required=True)
    description = graphene.String(required=True)
    company = graphene.String(required=True)
    job_type = graphene.String(required=True)
    location = graphene.String(required=True)
    latitude = graphene.Float()
    longitude = graphene.Float()
    salary_min = graphene.Float()
    salary_max = graphene.Float()
    category_id = graphene.UUID(required=True)


# -------------------------------
# Category Mutations
# -------------------------------

class CreateCategory(graphene.Mutation):
    class Arguments:
        name = graphene.String(required=True)

    category = graphene.Field(lambda: CategoryType)

    def mutate(self, info, name):
        user = info.context.user
        if user.is_anonymous or user.role.lower() != "admin":
            raise Exception("Unauthorised. User not an Admin!")
        category = JobCategory.objects.create(name=name)
        return CreateCategory(category=category)


# -------------------------------
# Job Mutations
# -------------------------------

class CreateJob(graphene.Mutation):
    class Arguments:
        input = JobInput(required=True)

    job = graphene.Field(lambda: JobType)
    success = graphene.Boolean()

    def mutate(self, info, input):
        # Admin validation will be added later
        user = info.context.user
        if user.is_anonymous or user.role.lower() != "admin":
            raise Exception("Unauthorised. User not an Admin!")
        category = get_object_or_404(JobCategory, pk=input.category_id)
        posted_by = get_object_or_404(User, pk=user.id)

        job = Job.objects.create(
            title=input.title,
            description=input.description,
            company=input.company,
            job_type=input.job_type,
            location=input.location,
            latitude=input.latitude,
            longitude=input.longitude,
            salary_min=input.salary_min,
            salary_max=input.salary_max,      
            category=category,
            posted_by=posted_by
        )

        return CreateJob(job=job, success=True)


class UpdateJob(graphene.Mutation):
    class Arguments:
        id = graphene.UUID(required=True)
        input = JobInput(required=True)

    job = graphene.Field(JobType)
    success = graphene.Boolean()

    def mutate(self, info, id, input):
        user = info.context.user
        if user.is_anonymous or user.role.lower() != "admin":
            raise Exception("Unauthorised. User not an Admin!")
        
        job = get_object_or_404(Job, pk=id)
        category = get_object_or_404(JobCategory, pk=input.category_id)

        for field, value in input.items():
            if field == "category_id":
                job.category = category
            else:
                setattr(job, field, value)

        job.save()
        return UpdateJob(job=job, success=True)


class DeleteJob(graphene.Mutation):
    class Arguments:
        id = graphene.UUID(required=True)

    success = graphene.Boolean()

    def mutate(self, info, id):
        user = info.context.user
        if user.is_anonymous or user.role.lower() != "admin":
            raise Exception("Unauthorised. User not an Admin!")
        
        job = get_object_or_404(Job, pk=id)
        job.delete()
        return DeleteJob(success=True)


