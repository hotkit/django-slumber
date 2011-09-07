from django.http import HttpResponse


def ok_text(request):
    return HttpResponse("ok", 'text/plain')
