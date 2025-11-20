import graphene
import graphql_jwt
from graphene_django.debug import DjangoDebug
from users.schema import UserQuery
from jobs.schema import (
    JobQuery, CreateJob, 
    UpdateJob, DeleteJob, 
    CreateCategory
)

from applications.schema import (
    ApplicationQuery,
    ApplyForJob,
    UpdateApplicationStatus,
)


class Query(
    UserQuery,
    JobQuery,
    ApplicationQuery,
    graphene.ObjectType
):
    pass


class Mutation(graphene.ObjectType):
    # login
    token_auth = graphql_jwt.ObtainJSONWebToken.Field()
    # refresh token
    refresh_token = graphql_jwt.Refresh.Field()
    # verify token
    verify_token = graphql_jwt.Verify.Field()

    # core mutations
    create_job = CreateJob.Field()
    update_job = UpdateJob.Field()
    delete_job = DeleteJob.Field()
    create_category = CreateCategory.Field()

    apply_for_job = ApplyForJob.Field()
    update_application_status = UpdateApplicationStatus.Field()


schema = graphene.Schema(query=Query, mutation=Mutation)
