from django.contrib.auth.views import get_user_model
from rest_framework.generics import GenericAPIView
from rest_framework.response import Response

from accounts.serializers import UserRegisterSerializer

User = get_user_model()


class RegisterAPIView(GenericAPIView):
    serializer_class = UserRegisterSerializer

    def post(self, request):
        serializer = self.get_serializer(data=request.data)

        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)

        return Response(serializer.errors)