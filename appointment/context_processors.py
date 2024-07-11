from .models import Services

def base_context(request):
    servicess = Services.objects.all()
    return {'servicess': servicess}