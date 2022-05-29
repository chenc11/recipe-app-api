"""
Views for the recipe APIs
"""
from drf_spectacular.utils import (
    extend_schema_view,
    extend_schema,
    OpenApiParameter,
    OpenApiTypes,
)
from rest_framework import (
    viewsets,
    mixins,  # mix in to a view to add additional functionality
    status,
)
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated
from core.models import (
    Recipe,
    Tag,
    Ingredient
)
from recipe import serializers


# extend the auto-generated schema created by Django Rest Spectacular
@extend_schema_view(
    # extend the schema for the list endpoint (where we add filters to)
    list=extend_schema(
        # define the params that can be passed to the requests
        # that made to the list API for this view
        parameters=[
            OpenApiParameter(
                'tags',
                OpenApiTypes.STR,  # specify the type to be string
                description='Comma separated list of tag IDs to filter',
            ),
            OpenApiParameter(
                'ingredients',
                OpenApiTypes.STR,
                description='Comma separated list of ingredient IDs to filter',
            ),
        ]
    )
)
class RecipeViewSet(viewsets.ModelViewSet):
    """View for manage recipe APIs."""
    serializer_class = serializers.RecipeDetailSerializer
    # objects available for this viewset
    queryset = Recipe.objects.all()
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def _params_to_ints(self, qs):
        """Convert a list of strings to integers."""
        # 1,2,3 -> iterate each integer separated by commas
        return [int(str_id) for str_id in qs.split(',')]

    def get_queryset(self):
        """Retrieve recipes for authenticated user."""
        # retrieving query params called tags and ingredients
        # result will be a comma separated list provided as a string
        tags = self.request.query_params.get('tags')
        ingredients = self.request.query_params.get('ingredients')
        # allow to apply filters to the query set
        # and return the resulting filtered output
        queryset = self.queryset
        if tags:
            tag_ids = self._params_to_ints(tags)
            # filter out tags by ID if any IDs in the list of tag we have
            queryset = queryset.filter(tags__id__in=tag_ids)
        if ingredients:
            ingredient_ids = self._params_to_ints(ingredients)
            queryset = queryset.filter(ingredients__id__in=ingredient_ids)

        # filter only recipes of the user assigned to the request
        # distinct() because recipes that has
        # multiple tags can be queried duplicate times when querying
        # multiple tags at the same time
        return queryset.filter(
            user=self.request.user
        ).order_by('-id').distinct()

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
        elif self.action == 'upload_image':
            return serializers.RecipeImageSerializer

        return self.serializer_class

    # overwrite perform_create to assign the user associated with the recipe
    # when we perform a creation of a new object through this model view,
    # create the following method as part of that object creation
    def perform_create(self, serializer):
        """Create a new recipe."""
        serializer.save(user=self.request.user)

    # apply this customized action to just the detail end point
    # i.e. a specific recipe
    @action(methods=['POST'], detail=True, url_path='upload-image')
    def upload_image(self, request, pk=None):
        """Upload an image to recipe."""
        recipe = self.get_object()
        serializer = self.get_serializer(recipe, data=request.data)

        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@extend_schema_view(
    list=extend_schema(
        parameters=[
            OpenApiParameter(
                'assigned_only',
                # can only assign 0 or 1 to this API
                OpenApiTypes.INT, enum=[0, 1],
                description='Filter by items assigned to recipes.',
            ),
        ]
    )
)
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
        # boolean function here to convert the 1 or 0
        # to true or false, set default value to 0 - false
        # specify the default is not providing filter
        assigned_only = bool(
            int(self.request.query_params.get('assigned_only', 0))
        )
        queryset = self.queryset
        if assigned_only:  # apply additional filter to queryset
            # filter recipes associated with the value
            queryset = queryset.filter(recipe__isnull=False)

        return queryset.filter(
            user=self.request.user
        ).order_by('-name').distinct()


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
