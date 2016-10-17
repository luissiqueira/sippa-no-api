from django.views.decorators.http import require_GET, require_POST

from business.wrapper import SIPPAWrapper
from django.http.response import JsonResponse


@require_GET
def start_login(request):
    return JsonResponse(SIPPAWrapper().start_auth())


@require_POST
def process_login(request):
    sippa = SIPPAWrapper()

    session = request.POST.get('session')
    login = request.POST.get('login')
    password = request.POST.get('password')
    captcha_value = request.POST.get('captcha_value')

    response = sippa.run(session=session, login=login, password=password, captcha_value=captcha_value)

    return JsonResponse(response)
