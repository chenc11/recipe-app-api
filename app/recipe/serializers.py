"""
Serializers for recipe APIs
"""
from rest_framework import serializers

from core.models import (
    Recipe,
    Tag,
    Ingredient
)


class IngredientSerializer(serializers.ModelSerializer):
    """Serializer for ingredients."""

    class Meta:
        model = Ingredient
        fields = ['id', 'name']
        read_only_fields = ['id']


class TagSerializer(serializers.ModelSerializer):
    """Serializer for tags."""

    class Meta:
        model = Tag
        fields = ['id', 'name']
        read_only_fields = ['id']


class RecipeSerializer(serializers.ModelSerializer):
    """Serializer for recipes."""
    tags = TagSerializer(many=True, required=False) # can be a list of tags and tag is not requried
    ingredients = IngredientSerializer(many=True, required=False)

    class Meta:
        model = Recipe
        fields = [
            'id', 'title', 'time_minutes', 'price', 'link', 'tags',
            'ingredients',
        ] # fields that can be seen in serializer
        read_only_fields = ['id']

    def _get_or_create_tags(self, tags, recipe):
        """Handle getting or creating tags as needed."""
        auth_user = self.context['request'].user # context is passed to the serializer by the view
        # loops through all the tags we poped from the validated data
        for tag in tags:
            # retrieve the tags if already existed in the database for authenticated user
            # if not existed, create a value with the value we passed in
            # so we won't get duplicate tags
            # created: true or false; if being created or fetched
            tag_obj, created = Tag.objects.get_or_create(
                user=auth_user,
                **tag,
            )
            recipe.tags.add(tag_obj)


    # _ means the method to be internal only so that won't be accidentally make call to it directly
    def _get_or_create_ingredients(self, ingredients, recipe):
        """Handle getting or creating ingredients as needed."""
        auth_user = self.context['request'].user
        for ingredient in ingredients:
            # get existing ingredients from or create new ingredients in the database
            ingredient_obj, created = Ingredient.objects.get_or_create(
                user=auth_user,
                **ingredient,
            )
            recipe.ingredients.add(ingredient_obj) # assign ingredients to the ingredients list


    def create(self, validated_data):
        """Create a recipe."""
        # if tags are existed in the validated data and then remove it from validated data and assign it to a new variable called tags
        # if doesn't exist, default to empty list
        tags = validated_data.pop('tags', [])
        ingredients = validated_data.pop('ingredients', [])
        recipe = Recipe.objects.create(**validated_data) # remove the tags before created the recipe
        # tags is a related field and is expected to be created separately and added as a relationship to recipe
        self._get_or_create_tags(tags, recipe)
        self._get_or_create_ingredients(ingredients, recipe)
        return recipe


    # override the update function to allow creating new objects in the field
    def update(self, instance, validated_data): # the existing instance and validated data that we want to pass to
        """Update recipe."""
        tags = validated_data.pop('tags', None)
        if tags is not None:
            instance.tags.clear()
            self._get_or_create_tags(tags, instance)

        # assign the values outside of tags to the instance
        for attr, value in validated_data.items():
            setattr(instance, attr, value)

        instance.save()
        return instance



# will be an extension of the the RecipeSerializer so take all functionality of RecipeSerializer and add extra fields
class RecipeDetailSerializer(RecipeSerializer):
    """Serializer for recipe detail view."""

    class Meta(RecipeSerializer.Meta):
        fields = RecipeSerializer.Meta.fields + ['description']
