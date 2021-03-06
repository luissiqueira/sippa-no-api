import msgpack
from django.views.decorators.csrf import csrf_exempt

from django.views.decorators.http import require_GET, require_POST

from business.wrapper import SIPPAWrapper
from django.http.response import JsonResponse, HttpResponse
from ratelimit.decorators import ratelimit


@require_GET
@ratelimit(key='ip', rate='15/20m')
def start_login(request):
    response = SIPPAWrapper().start_auth()
    response_format = request.GET.get('format', 'json')

    return dict_to_response(response, response_format)


@require_POST
@ratelimit(key='ip', rate='15/20m')
@csrf_exempt
def process_login(request):
    sippa = SIPPAWrapper()

    session = request.POST.get('session')
    login = request.POST.get('login')
    password = request.POST.get('password')
    captcha_value = request.POST.get('captcha_value')

    response = sippa.run(session=session, login=login, password=password, captcha_value=captcha_value)
    response_format = request.POST.get('format', 'json')

    return dict_to_response(response, response_format)


def dict_to_response(response, response_format):
    if response_format == 'msgpack':
        return HttpResponse(msgpack.packb(response))
    else:
        return JsonResponse(response)
