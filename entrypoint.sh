#!/bin/sh
set -e

SERVICE=${1:-web}

echo "🚀 Starting service: $SERVICE"

if [ "$SERVICE" = "web" ]; then
    echo "📦 Applying migrations..."
    python manage.py migrate --noinput

    echo "🎨 Collecting static files..."
    python manage.py collectstatic --noinput

    echo "👤 Creating superuser (admin/admin) if not exists..."
    python -c "
from django.contrib.auth import get_user_model
import django, os
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()
U = get_user_model()
if not U.objects.filter(username='admin').exists():
    U.objects.create_superuser('admin', 'admin@example.com', 'admin')
    print('  ✅ Superuser yaratildi: admin / admin')
else:
    print('  ⏭️  Superuser allaqachon mavjud')
"
    echo "🌐 Starting Django on 0.0.0.0:8000 ..."
    exec python manage.py runserver 0.0.0.0:8000

elif [ "$SERVICE" = "bot" ]; then
    echo "🤖 Starting Telegram bot..."
    exec python barber/bot.py

else
    echo "❌ Noma'lum servis: $SERVICE (web yoki bot bo'lishi kerak)"
    exit 1
fi
