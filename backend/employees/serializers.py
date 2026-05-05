import uuid
from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from django.contrib.auth import authenticate

from .models import Employee, Department


# ============================
# DEPARTMENT SERIALIZER
# ============================

class DepartmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Department
        fields = ["id", "name", "description"]


# ============================
# EMPLOYEE SERIALIZER
# ============================

class EmployeeSerializer(serializers.ModelSerializer):

    department = serializers.SerializerMethodField()
    manager_name = serializers.SerializerMethodField()
    department_id = serializers.PrimaryKeyRelatedField(
        queryset=Department.objects.all(),
        source="department",
        write_only=True,
        required=False,
        allow_null=True,
    )
    manager_id = serializers.PrimaryKeyRelatedField(
        queryset=Employee.objects.all(),
        source="manager",
        write_only=True,
        required=False,
        allow_null=True,
    )

    def get_department(self, obj):
        if obj.department:
            return {
                "id": obj.department.id,
                "name": obj.department.name,
            }
        return None

    def get_manager_name(self, obj):
        if obj.manager:
            return f"{obj.manager.first_name} {obj.manager.last_name}"
        return None

    class Meta:
        model = Employee

        fields = [
            "id",
            "username",
            "email",
            "first_name",
            "last_name",
            "employee_id",

            "department",
            "department_id",

            "position",
            "hire_date",
            "phone_number",
            "photo_url",

            # balances
            "cp_balance",
            "rtt_balance",

            "manager",
            "manager_name",
            "manager_id",

            "role",
            "is_active",
        ]

        read_only_fields = [
            "id",
            "cp_balance",
            "rtt_balance",
        ]


# ============================
# REGISTER SERIALIZER
# ============================

class RegisterSerializer(serializers.ModelSerializer):

    password = serializers.CharField(write_only=True)
    confirm_password = serializers.CharField(write_only=True)

    class Meta:
        model = Employee
        fields = ["username", "email", "password", "confirm_password"]

    def validate(self, data):
        if data["password"] != data["confirm_password"]:
            raise serializers.ValidationError("Passwords do not match")
        return data

    def create(self, validated_data):

        validated_data.pop("confirm_password")

        employee_id = f"EMP-{uuid.uuid4().hex[:8]}"

        user = Employee.objects.create_user(
            username=validated_data["username"],
            email=validated_data["email"],
            password=validated_data["password"],
            employee_id=employee_id,
        )

        user.is_active = False
        user.save()

        return user


# ============================
# LOGIN SERIALIZER
# ============================

class LoginSerializer(serializers.Serializer):

    username = serializers.CharField()
    password = serializers.CharField(write_only=True)

    def validate(self, data):

        user = authenticate(
            username=data.get("username"),
            password=data.get("password"),
        )

        if user is None:
            raise serializers.ValidationError("Invalid username or password.")

        if not user.is_active:
            raise serializers.ValidationError(
                "This user account is inactive. Please wait for admin approval."
            )

        token_serializer = TokenObtainPairSerializer(data={
            "username": data["username"],
            "password": data["password"],
        })

        token_serializer.is_valid(raise_exception=True)

        return {
            "user": user,
            "refresh": token_serializer.validated_data["refresh"],
            "access": token_serializer.validated_data["access"],
        }
