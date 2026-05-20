#!/bin/sh
set -e

SERVICE=${1:-web}

echo "🚀 Starting CRM service: $SERVICE"

if [ "$SERVICE" = "web" ]; then
    echo "📦 Applying database migrations..."
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
    print('  ✅ Superuser created: admin / admin')
else:
    print('  ⏭️  Superuser already exists')
"
    echo "🔧 Env check..."
    python -c "import core.envs; print(core.envs.env_debug_summary())"

    echo "🌐 Starting Daphne ASGI Server on 0.0.0.0:8000..."
    exec daphne -b 0.0.0.0 -p 8000 config.asgi:application

elif [ "$SERVICE" = "worker" ]; then
    echo "⚙️ Starting Celery Worker..."
    exec celery -A config worker -l info

elif [ "$SERVICE" = "beat" ]; then
    echo "⏰ Starting Celery Beat Scheduler..."
    # Ensure any old celery beat pid file is cleaned up before starting
    rm -f celerybeat.pid
    exec celery -A config beat -l info

elif [ "$SERVICE" = "bot" ]; then
    echo "🤖 Starting Standalone Telegram Bot..."
    exec python integrations/telegram/bot.py

else
    echo "❌ Unknown service: $SERVICE (must be web, worker, beat, or bot)"
    exit 1
fi
