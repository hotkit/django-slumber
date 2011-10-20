from django.http import HttpResponse


def _ok_text(request):
    # Patch this if we want to patch the view function
    return HttpResponse("ok", 'text/plain')
def ok_text(request):
    return _ok_text(request)
