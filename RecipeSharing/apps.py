from django.apps import AppConfig

class RecipesharingConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'RecipeSharing'

    def ready(self):
        import RecipeSharing.signals