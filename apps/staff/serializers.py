from rest_framework import serializers
from django.contrib.auth.models import User
from .models import Staff, Barbershop, BarberSchedule

class StaffSerializer(serializers.ModelSerializer):
    class Meta:
        model = Staff
        fields = [
            "id",
            "barbershop",
            "first_name",
            "last_name",
            "phone",
            "role",
            "telegram_id",
            "is_active",
            "created_at",
        ]
        read_only_fields = ["id", "created_at"]


class BarberSignupSerializer(serializers.Serializer):
    username = serializers.CharField(max_length=150)
    password = serializers.CharField(write_only=True)
    first_name = serializers.CharField(max_length=100)
    last_name = serializers.CharField(max_length=100, required=False, default="")
    phone = serializers.CharField(max_length=20)
    barbershop_name = serializers.CharField(max_length=200, required=False)
    barbershop_id = serializers.IntegerField(required=False)

    def validate_username(self, value):
        if User.objects.filter(username=value).exists():
            raise serializers.ValidationError("Ushbu foydalanuvchi nomi band.")
        return value

    def validate_phone(self, value):
        if Staff.objects.filter(phone=value).exists():
            raise serializers.ValidationError("Ushbu telefon raqamli sartarosh ro'yxatdan o'tgan.")
        return value

    def create(self, validated_data):
        username = validated_data["username"]
        password = validated_data["password"]
        first_name = validated_data["first_name"]
        last_name = validated_data["last_name"]
        phone = validated_data["phone"]

        # Handle barbershop branch
        barbershop = None
        b_name = validated_data.get("barbershop_name")
        b_id = validated_data.get("barbershop_id")
        if b_name:
            barbershop = Barbershop.objects.create(name=b_name, address="Toshkent shahri")
        elif b_id:
            try:
                barbershop = Barbershop.objects.get(id=b_id)
            except Barbershop.DoesNotExist:
                raise serializers.ValidationError({"barbershop_id": "Tanlangan sartaroshxona topilmadi."})
        else:
            barbershop, _ = Barbershop.objects.get_or_create(
                name="Asosiy Sartaroshxona",
                defaults={"address": "Toshkent shahri"}
            )

        # Create Django user
        user = User.objects.create_user(
            username=username,
            password=password,
            first_name=first_name,
            last_name=last_name
        )

        # Create Staff profile
        staff = Staff.objects.create(
            user=user,
            barbershop=barbershop,
            first_name=first_name,
            last_name=last_name,
            phone=phone,
            role="barber"
        )
        return staff


class BarberScheduleSerializer(serializers.ModelSerializer):
    class Meta:
        model = BarberSchedule
        fields = ["id", "staff", "date", "is_working", "start_time", "end_time"]
        read_only_fields = ["id"]


class BarbershopSerializer(serializers.ModelSerializer):
    class Meta:
        model = Barbershop
        fields = ["id", "name", "address", "latitude", "longitude"]


