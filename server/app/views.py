from app.models import File, User, Share
from app.utils import get_hashed_pass
from app.utils import need_authorization
from django.http import JsonResponse, HttpResponse
from rest_framework.response import Response
from rest_framework.views import APIView


class FileView(APIView):

    @need_authorization
    def get(self, request, token):
        try:
            file = File.objects.get(token=token)
        except File.DoesNotExist:
            return Response(status=404)
        return Response(dict(data=file.data))

    def post(self, request):
        file = File.objects.create(data=None)
        return Response(dict(token=file.token, write_key=file.write_key))

    @need_authorization
    def put(self, request, token):
        try:
            file = File.objects.get(token=token)
        except File.DoesNotExists:
            return Response(status=404)
        if file.write_key != request.POST['write_key']:
            return Response(status=403)
        data = request.POST['data']
        file.data = data
        file.save()
        return Response(dict(data=file.data))

    @need_authorization
    def delete(self, request, token):
        try:
            file = File.objects.get(token=token)
        except File.DoesNotExist:
            return Response(status=404)
        if file.write_key != request.POST['write_key']:
            return Response(status=403)
        file.delete()
        return Response()


class ShareView(APIView):
    @need_authorization
    def get(self, request):
        shares = Share.objects.filter(to_user=request.user)
        result = [(share.file_id, share.data) for share in shares]
        return Response(data=result)

    @need_authorization
    def post(self, request):
        to_username = request.POST['username']
        token = request.POST['token']
        data = request.POST['data']
        try:
            to_user = User.objects.get(user_name=to_username)
        except User.DoesNotExist:
            return Response(status=404)
        Share.objects.create(to_user=to_user, file_id=token, data=data)
        return Response(status=201)


def login(request):
    user_name = request.POST.get('user_name')
    password = request.POST.get('password')
    try:
        user = User.objects.get(user_name=user_name)
    except User.DoesNotExist:
        return HttpResponse(status=404)
    if user.password != get_hashed_pass(password):
        return HttpResponse(status=401)
    root_file = File.objects.get(token=user.root_token)
    return JsonResponse(
        dict(authorization=user.get_authorization(), root_token=user.root_token, root_write_key=root_file.write_key))


def signup(request):
    first_name = request.POST.get('first_name')
    last_name = request.POST.get('last_name')
    user_name = request.POST.get('user_name')
    password = request.POST.get('password')
    root_token = request.POST.get('root_token')
    public_key = request.POST.get('public_key')
    user = User.objects.create(first_name=first_name, last_name=last_name, user_name=user_name,
                               password=get_hashed_pass(password), root_token=root_token, public_key=public_key)
    return JsonResponse(dict(authorization=user.get_authorization(), root_token=user.root_token))


def get_user_public(request, user_name):
    try:
        user = User.objects.get(user_name=user_name)
    except User.DoesNotExist:
        return HttpResponse(status=404)
    return JsonResponse(dict(user_name=user.user_name, public_key=user.public_key))
