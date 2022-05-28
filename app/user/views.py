"""
Views for the user API.
"""
from rest_framework import generics, authentication, permissions
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.settings import api_settings


from user.serializers import (
    UserSerializer,
    AuthTokenSerializer,
)


class CreateUserView(generics.CreateAPIView):
    """Create a new user in the system."""
    serializer_class = UserSerializer


class CreateTokenView(ObtainAuthToken):
    """Create a new auth token for user."""
    serializer_class = AuthTokenSerializer
    renderer_classes = api_settings.DEFAULT_RENDERER_CLASSES


class ManageUserView(generics.RetrieveUpdateAPIView):
    """Manage the authenticated user."""
    serializer_class = UserSerializer
    #make sure the user actually exists
    authentication_classes = [authentication.TokenAuthentication]
    #the user is authenticated to use this api
    permission_classes = [permissions.IsAuthenticated]

    # overwrite get_object (any http requests made to the API): only
    # retrieving the user attached to the request
    # made http get request to this endpoint ->
    # call get_object to get the user ->
    # retrieve the user that was authenticated ->
    # run through serializer before returning result to API
    def get_object(self):
        """Retrieve and return the authenticated user."""
        return self.request.user
