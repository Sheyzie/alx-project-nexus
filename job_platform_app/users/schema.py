import graphene
from graphene_django import DjangoObjectType
from django.contrib.auth import get_user_model

from .models import Profile


User = get_user_model()


class ProfileType(DjangoObjectType):
    class Meta:
        model = Profile
        fields = ("id", "fullname", "headline", "bio", "phone_number", "location", "resume_url", "skill", "visibility")


class UserType(DjangoObjectType):
    class Meta:
        model = User
        fields = ("id", "email", "profile", "role", "date_joined")


class UserQuery(graphene.ObjectType):
    users = graphene.List(UserType)
    user = graphene.Field(UserType, id=graphene.UUID(required=True))

    def resolve_users(root, info):
        # print("META HEADER:", info.context.META.get("HTTP_AUTHORIZATION"))
        # print("HEADERS:", info.context.headers)
        user = info.context.user
        if user.is_anonymous:
            raise Exception("User not logged in!")
        
        return User.objects.all()

    def resolve_user(root, info, id):
        user = info.context.user
        if user.is_anonymous:
            raise Exception("User not logged in!")
        
        return User.objects.get(pk=id)
    



