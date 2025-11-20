from graphene_django.views import GraphQLView
from django.contrib.auth.mixins import LoginRequiredMixin


class DjangoContextGraphQLView(GraphQLView):
    def get_context(self, request):
        # return the actual Django request, not a wrapper
        return request

    def get_graphql_params(self, request, data):
        params = super().get_graphql_params(request, data)
        # Inject headers manually into context
        auth_header = request.headers.get("Authorization")
        if auth_header:
            request.META["HTTP_AUTHORIZATION"] = auth_header
        return params


# class DjangoContextGraphQLView(GraphQLView):
#     graphiql = True
#     graphiql_template = "graphene/graphiql.html"
#     graphiql_version = "1.0.3"
#     graphiql_fetcher = '''function graphQLFetcher(params) {
#         return fetch('/graphql/', {
#             method: 'post',
#             headers: {
#                 'Content-Type': 'application/json',
#                 'Authorization': localStorage.getItem('graphql_auth') || '',
#             },
#             body: JSON.stringify(params)
#         }).then(r => r.json());
#     }'''

#     def get_context(self, request):
#         return request

#     def get_graphql_params(self, request, data):
#         params = super().get_graphql_params(request, data)

#         # read from request header if GraphiQL actually sends anything
#         auth = request.headers.get("Authorization")
#         if auth:
#             request.META["HTTP_AUTHORIZATION"] = auth

#         return params

