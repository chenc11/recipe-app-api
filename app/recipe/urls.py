"""
URL mappings for the recipe app.
"""
from django.urls import (
    path,
    include,
)

from rest_framework.routers import DefaultRouter

from recipe import views


router = DefaultRouter()
router.register('recipes', views.RecipeViewSet) # create a new endpint /recipe and assign all different endpoints from recipe viewset to that endpoint
# the recipe viewset is going to have auto generated URLs depending on the functionality enabled on the view set
# and because of we use the base model viewset, we can access to all the get, post, delete, patch, put endpoints
router.register('tags', views.TagViewSet)
router.register('ingredients', views.IngredientViewSet)

app_name = 'recipe'

urlpatterns = [
    path('', include(router.urls)),
]
