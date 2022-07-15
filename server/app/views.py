from app.models import File, User
from app.utils import get_hashed_pass
from app.utils import need_authorization
from rest_framework.response import Response
from rest_framework.views import APIView
from django.http import JsonResponse, HttpResponse


class FileView(APIView):

    @need_authorization
    def get(self, request, token):
        try:
            file = File.objects.get(token=token)
        except File.DoesNotExist:
            return Response(status=404)
        return Response(dict(data=file.data))

    def post(self, request):
        data = request.POST['data']
        file = File.objects.create(data=data)
        return Response(dict(token=file.token))

    @need_authorization
    def put(self, request, token):
        try:
            file = File.objects.get(token=token)
        except File.DoesNotExists:
            return Response(status=404)
        data = request.POST['data']
        file.data = data
        file.save()
        return Response(dict(data=file.data))

    @need_authorization
    def delete(self, request, token):
        try:
            File.objects.get(token=token).delete()
        except File.DoesNotExist:
            return Response(status=404)
        return Response()


def login(request):
    user_name = request.POST.get('user_name')
    password = request.POST.get('password')
    try:
        user = User.objects.get(user_name=user_name)
    except User.DoesNotExist:
        return HttpResponse(status=404)
    if user.password != get_hashed_pass(password):
        return HttpResponse(status=401)
    return JsonResponse(dict(authorization=user.get_authorization(), root_token=user.root_token))


def signup(request):
    first_name = request.POST.get('first_name')
    last_name = request.POST.get('last_name')
    user_name = request.POST.get('user_name')
    password = request.POST.get('password')
    root_token = request.POST.get('root_token')
    User.objects.create(first_name=first_name, last_name=last_name, user_name=user_name,
                        password=get_hashed_pass(password), root_token=root_token)
    return HttpResponse(status=201)
