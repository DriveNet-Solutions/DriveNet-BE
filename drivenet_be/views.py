from rest_framework.authtoken.models import Token
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.authentication import authenticate
from django.contrib.auth import login, logout
from rest_framework.permissions import IsAuthenticated
from django.contrib.auth.models import User, Group

class LoginView(APIView):
    def post(self, request):
        print(request.data)
        username = request.data.get('username')
        password = request.data.get('password')
        user= authenticate(username=username, password=password)
        if user is not None:
            login(request,user)
            if user.groups.filter(name='Admin').exists():
                return Response({'message' : 'Inicio de sesión exitoso de admin', 'redirectUrl' : '/admin'}, status=200)
            else:
                return Response({'message' : 'NO es admin'}, status=400)
        else:
            return Response({'message' : 'Inicio de sesión inválido'}, status=400)

class LogoutView(APIView):
    def post(self, request):
        logout(request)
        return Response ({'message' : 'Sesión cerrada correctamente'}, status=200)

class showEmployeeView(APIView):
    permission_classes = [IsAuthenticated]
    def get(self, request):
        users = User.objects.all()
        data = [
            {
                'id': user.id,
                'username': user.username,
                'first_name': user.first_name,
                'last_name': user.last_name ,
                'email': user.email,
                'role': user.groups.first().name  if user.groups.exists() else 'No role',
            }
            for user in users
        ]
        return Response(data, status=200)

class addEmployeeView(APIView):
    def post (self, request):
        username = request.data.get('username')
        email = request.data.get('email')
        first_name = request.data.get('first_name')
        last_name = request.data.get('last_name')
        password = request.data.get('password')
        role = request.data.get('role')
        try:
            user = User.objects.create_user(username=username, email=email, password=password, last_name= last_name, first_name=first_name)
            group = Group.objects.get(name=role)
            user.groups.add(group)
            user.save()
            return Response({'message' : 'Empleado agregado correctamente'}, status=200)
        except Exception as e:
            return Response({'message' : str(e)}, status=400)

class editEmployeeView(APIView):
    def put(self,request,user_id):
        try:
            user = User.objects.get(id=user_id)
            user.username = request.data.get('username', user.username)
            user.email = request.data.get('email', user.email)
            user.first_name = request.data.get('first_name', user.first_name)
            user.last_name = request.data.get('last_name', user.last_name)
            new_role = request.data.get('role')
            if new_role:
                group = Group.objects.get(name=new_role)
                user.groups.clear()
                user.groups.add(group)
            user.save()
            return Response({'message' : 'Empleado actualizado correctamente'}, status=200)
        except User.DoesNotExist:
            return Response({'error': 'Empleado no encontrado'}, status=400)
        except Group.DoesNotExist:
            return Response({'error': f'El rol "{new_role}" no existe'}, status=400)
        except Exception as e:
            return Response({'error': str(e)}, status=400)

class removeEmployeeView(APIView):
    def delete(self, request, user_id):
        try:
            user = User.objects.get(id=user_id)
            user.delete()
            return Response({'message' : 'Empleado eliminado correctamente'}, status=200)
        except User.DoesNotExist:
            return Response({'error': 'Empleado no encontrado'}, status=400)
        except Exception as e:
            return Response({'error': str(e)}, status=400)




