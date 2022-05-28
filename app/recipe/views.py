"""
Views for the recipe APIs
"""
from rest_framework import (
    viewsets,
    mixins,  # mix in to a view to add additional functionality
)
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated
from core.models import (
    Recipe,
    Tag,
    Ingredient
)
from recipe import serializers


class RecipeViewSet(viewsets.ModelViewSet):
    """View for manage recipe APIs."""
    serializer_class = serializers.RecipeDetailSerializer
    # objects available for this viewset
    queryset = Recipe.objects.all()
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        """Retrieve recipes for authenticated user."""
        # filter only recipes of the user assigned to the request
        return self.queryset.filter(user=self.request.user).order_by('-id')

    # the method get called when RDF wants to determine the class
    # that's being used for a particular action
    # override this method so that when the user
    # is calling the detail endpoint,
    # we're going to use the detail serializer instead of the default
    # one that's configured the list view
    def get_serializer_class(self):
        """Return the serializer class for request."""
        if self.action == 'list':
            return serializers.RecipeSerializer

        return self.serializer_class

    # overwrite perform_create to assign the user associated with the recipe
    # when we perform a creation of a new object through this model view,
    # create the following method as part of that object creation
    def perform_create(self, serializer):
        """Create a new recipe."""
        serializer.save(user=self.request.user)


class BaseRecipeAttrViewSet(mixins.DestroyModelMixin,
                            mixins.UpdateModelMixin,
                            mixins.ListModelMixin,
                            viewsets.GenericViewSet):
    """Base viewset for recipe attributes."""
    # add support for token authentication and the
    # only authentication for this viewset
    authentication_classes = [TokenAuthentication]
    # all the user must be authenticated to use this endpoint
    permission_classes = [IsAuthenticated]

    # we only want users to view, update,
    # and make changes to their own ingredients
    def get_queryset(self):
        """Filter queryset to authenticated user."""
        return self.queryset.filter(user=self.request.user).order_by('-name')


# leverage viewset based class because the tag utilizes the CURD functionality
class TagViewSet(BaseRecipeAttrViewSet):
    """Manage tags in the database."""
    serializer_class = serializers.TagSerializer
    queryset = Tag.objects.all()


class IngredientViewSet(BaseRecipeAttrViewSet):
    """Manage ingredients in the database."""
    serializer_class = serializers.IngredientSerializer
    # tell Django what models we want to be
    # manageable through the ingredient viewset
    queryset = Ingredient.objects.all()
