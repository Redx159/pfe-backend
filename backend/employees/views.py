from rest_framework import generics, permissions, status, viewsets
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.views import TokenRefreshView
from .permissions import IsAdminOrHR



from .serializers import (
    EmployeeSerializer,
    LoginSerializer,
    RegisterSerializer,
    DepartmentSerializer,
)
from django.shortcuts import get_object_or_404
from django.core.mail import send_mail
from django.conf import settings
from rest_framework.permissions import IsAdminUser
from .models import Employee, Department


class LoginView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        serializer = LoginSerializer(data=request.data)

        if serializer.is_valid():
            user = serializer.validated_data['user']
            user_data = EmployeeSerializer(user).data

            return Response({
                'success': True,
                'message': 'Login successful',
                'user': user_data,
                'tokens': {
                    'refresh': serializer.validated_data['refresh'],
                    'access': serializer.validated_data['access']
                }
            })

        return Response({
            'success': False,
            'errors': serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)


# ============================
# SIGNUP VIEW (NEW)
# ============================

class RegisterView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        serializer = RegisterSerializer(data=request.data)

        if serializer.is_valid():
            serializer.save()
            return Response(
                {
                    'success': True,
                    'message': 'Account created. Waiting for admin approval.'
                },
                status=status.HTTP_201_CREATED
            )

        return Response(
            {
                'success': False,
                'errors': serializer.errors
            },
            status=status.HTTP_400_BAD_REQUEST
        )


class ProfileView(generics.RetrieveUpdateAPIView):
    serializer_class = EmployeeSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        return self.request.user


class RefreshTokenView(TokenRefreshView):
    permission_classes = [permissions.AllowAny]


class LogoutView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        return Response({
            'success': True,
            'message': 'Logout successful'
        })


class ApproveUserView(APIView):
    """Admin-only endpoint to approve (activate) a user account."""
    permission_classes = [IsAdminUser]

    def post(self, request, pk):
        user = get_object_or_404(Employee, pk=pk)

        if user.is_active:
            return Response({'success': False, 'message': 'User already active.'}, status=status.HTTP_400_BAD_REQUEST)

        user.is_active = True
        user.save()

        # send a simple notification email (uses configured EMAIL_BACKEND)
        if user.email:
            from_email = getattr(settings, 'DEFAULT_FROM_EMAIL', None) or getattr(settings, 'EMAIL_HOST_USER', None) or 'noreply@example.com'
            try:
                # Do not fail silently here — surface errors so caller can know if send failed
                send_mail(
                    'Your account has been approved',
                    'Hello,\n\nYour account has been approved by an administrator. You can now log in.',
                    from_email,
                    [user.email],
                    fail_silently=False,
                )
            except Exception as exc:
                # Roll back activation if email couldn't be delivered (optional safety)
                user.is_active = False
                user.save()
                return Response({'success': False, 'message': 'Failed to send approval email', 'error': str(exc)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        return Response({'success': True, 'message': 'User approved', 'user': EmployeeSerializer(user).data})
   
class EmployeeListView(generics.ListAPIView):
    queryset = Employee.objects.all()
    serializer_class = EmployeeSerializer
    permission_classes = [permissions.IsAuthenticated]

    


class DepartmentViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Department.objects.all()
    serializer_class = DepartmentSerializer
    permission_classes = [permissions.IsAuthenticated]


class EmployeeViewSet(viewsets.ModelViewSet):
    queryset = Employee.objects.all()
    serializer_class = EmployeeSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user

        if user.role in ("ADMIN", "HR"):
            return Employee.objects.all()

        return Employee.objects.filter(id=user.id)





class ApproveUserView(APIView):

    permission_classes = [IsAdminOrHR]

    def post(self, request, pk):

        user = get_object_or_404(Employee, pk=pk)

        if user.is_active:
            return Response(
                {"success": False, "message": "User already active."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        user.is_active = True
        user.save()

        return Response({
            "success": True,
            "message": "User approved",
            "user": EmployeeSerializer(user).data,
        })
