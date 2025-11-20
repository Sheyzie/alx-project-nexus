
class JWTDebugMiddleware:
    def resolve(self, next, root, info, **args):
        print(">>> CUSTOM DEBUG MIDDLEWARE HIT <<<")
        print("Context type:", type(info.context))
        print("META AUTH:", info.context.META.get("HTTP_AUTHORIZATION"))
        print("CONTEXT HEADERS:", info.context.headers)
        return next(root, info, **args)
