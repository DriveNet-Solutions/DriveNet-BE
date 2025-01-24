from django.contrib.auth.hashers import make_password
from django.db import IntegrityError
from rest_framework.authtoken.models import Token
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.authentication import authenticate
from django.contrib.auth import login
from rest_framework import status
from .models import User
from .serializer import UserSerializer
import logging
 
logger = logging.getLogger(__name__)

class LoginView(APIView):
    def post(self, request):
        print(request.data)
        username = request.data.get('username')
        password = request.data.get('password')
        user = authenticate(username=username, password=password)
        if user is not None:
            login(request, user)
            if user.groups.filter(name='Admin').exists():
                return Response({'message' : 'Inicio de sesión exitoso de admin', 'redirectUrl' : '/admin'}, status=200)
                return Response({'message': 'Inicio de sesión exitoso de admin', 'redirectUrl':'/user-search'}, status=200)
            else:
                return Response({'message': 'NO es admin'}, status=400)
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
            return Response({'message': 'Inicio de sesión inválido'}, status=400)

class UserSearchView(APIView):
    def get(self, request):
        cedula = request.query_params.get('id')
        logger.debug(f"Searching for user with ID: {cedula}")
        if not cedula:
            logger.warning("No ID provided for search.")
            return Response({"error": "A valid ID must be provided"}, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            user = User.objects.get(id=cedula)
            serializer = UserSerializer(user)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except User.DoesNotExist:
            logger.error(f"User with ID {cedula} not found.")
            return Response({"error": "User not found"}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            logger.error(f"Internal error: {str(e)}")
            return Response({"error": f"Internal error: {str(e)}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def post(self, request):
        logger.debug("Attempting to add a new user.")
        serializer = UserSerializer(data=request.data)
        if serializer.is_valid():
            try:
                serializer.save()
                logger.info("User added successfully.")
                return Response(serializer.data, status=status.HTTP_201_CREATED)
            except IntegrityError as e:
                logger.error(f"Integrity error: {str(e)}")
                return Response({"error": "ID or Email must be unique."}, status=status.HTTP_400_BAD_REQUEST)
            except Exception as e:
                logger.error(f"Error saving user: {str(e)}")
                return Response({"error": f"Internal error: {str(e)}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        logger.error(f"Invalid data: {serializer.errors}")
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def put(self, request):
        cedula = request.data.get('id')
        logger.debug(f"Attempting to edit user with ID: {cedula}")
        if not cedula:
            logger.warning("No ID provided for edit.")
            return Response({"error": "A valid ID must be provided to edit"}, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            user = User.objects.get(id=cedula)
            serializer = UserSerializer(user, data=request.data, partial=True)
            if serializer.is_valid():
                serializer.save()
                logger.info("User updated successfully.")
                return Response(serializer.data, status=status.HTTP_200_OK)
            logger.error(f"Invalid data: {serializer.errors}")
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except User.DoesNotExist:
            logger.error(f"User with ID {cedula} not found.")
            return Response({"error": "User not found"}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            logger.error(f"Internal error: {str(e)}")
            return Response({"error": f"Internal error: {str(e)}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def delete(self, request):
        cedula = request.query_params.get('id')
        logger.debug(f"Attempting to delete user with ID: {cedula}")
        if not cedula:
            logger.warning("No ID provided for deletion.")
            return Response({"error": "A valid ID must be provided to delete"}, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            user = User.objects.get(id=cedula)
            user.delete()
            logger.info(f"User with ID {cedula} deleted successfully.")
            return Response({"message": "User deleted successfully"}, status=status.HTTP_200_OK)
        except User.DoesNotExist:
            logger.error(f"User with ID {cedula} not found.")
            return Response({"error": "User not found"}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            logger.error(f"Internal error: {str(e)}")
            return Response({"error": f"Internal error: {str(e)}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
