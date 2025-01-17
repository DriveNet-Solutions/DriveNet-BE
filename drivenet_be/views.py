from rest_framework.authtoken.models import Token
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.authentication import authenticate
from django.contrib.auth import login

class LoginView(APIView):
    def post(self, request):
        print(request.data)
        username = request.data.get('username')
        password = request.data.get('password')
        user= authenticate(username=username, password=password)
        if user is not None:
            login(request,user)
            if user.groups.filter(name='Admin').exists():
                return Response({'message' : 'Inicio de sesión exitoso de admin'}, status=200)
            else:
                return Response({'message' : 'NO es admin'}, status=400)
        else:
            return Response({'message' : 'Inicio de sesión inválido'}, status=400)