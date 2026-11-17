from .models import Animal


def petfeed_context(request):
    """Общие данные для всех шаблонов (выводятся в подвале base.html)."""
    return {
        "site_name": "PetFeed",
        "animals_count": Animal.objects.count(),
    }
