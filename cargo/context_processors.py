from .config import SITE_NAME
def site_name(request):
    return {'site_name': SITE_NAME}