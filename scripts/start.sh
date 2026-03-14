#!/bin/bash

# Цвета для вывода
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

print_step() { echo -e "${BLUE}▶ $1${NC}"; }
print_success() { echo -e "${GREEN}✔ $1${NC}"; }
print_error() { echo -e "${RED}✖ $1${NC}"; }
print_warning() { echo -e "${YELLOW}⚠ $1${NC}"; }

check_status() {
    if [ $? -ne 0 ]; then
        print_error "$1"
        exit 1
    fi
}

echo -e "${GREEN}"
echo "╔════════════════════════════════════════╗"
echo "║     Blog API - Automated Setup         ║"
echo "╚════════════════════════════════════════╝"
echo -e "${NC}"

# Переход в корень проекта
cd "$(dirname "$0")/.." || exit 1

# 1. Проверка переменных окружения
# ============================================
print_step "Проверка переменных окружения..."

# Твой файл находится в settings/.env по логам
ENV_FILE="settings/.env"

if [ ! -f "$ENV_FILE" ]; then
    print_error "Файл $ENV_FILE не найден!"
    exit 1
fi

# Список переменных, которые скрипт ругался, что они пустые
required_vars=(
    "SECRET_KEY"
    "BLOG_DEBUG"
)

for var in "${required_vars[@]}"; do
    value=$(grep "^${var}=" "$ENV_FILE" | cut -d '=' -f2- | xargs)
    if [ -z "$value" ]; then
        print_error "Переменная $var отсутствует или пуста в $ENV_FILE"
        exit 1
    fi
done
print_success "Переменные окружения в порядке"

# 2. Виртуальное окружение
# ============================================
if [ ! -d "venv" ]; then
    print_step "Создание venv..."
    python3 -m venv venv
    check_status "Не удалось создать venv"
fi
source venv/bin/activate

# 3. Установка зависимостей
# ============================================
print_step "Установка зависимостей..."
pip install --upgrade pip -q
# Если у тебя requirements.txt в корне, используй его
if [ -f "requirements.txt" ]; then
    pip install -r requirements.txt -q
else
    # Если они в папке, как в твоем примере
    pip install -r requirements/dev.txt -q
fi
check_status "Ошибка установки зависимостей"

# 4. Миграции и Статика
# ============================================
print_step "Миграции и статика..."
python manage.py migrate --noinput && python manage.py collectstatic --noinput -c
check_status "Ошибка БД или статики"

# 5. Переводы
# ============================================
print_step "Компиляция переводов..."
python manage.py compilemessages || print_warning "gettext не установлен, пропуск"

# 6. Создание суперпользователя (Админ)
# ============================================
print_step "Проверка суперпользователя..."
SUPERUSER_EMAIL="admin@blog-api.com"
SUPERUSER_PASS="admin123"

python manage.py shell << EOF
from apps.users.models import CustomUser
if not CustomUser.objects.filter(email='$SUPERUSER_EMAIL').exists():
    CustomUser.objects.create_superuser(
        username='admin',
        email='$SUPERUSER_EMAIL',
        password='$SUPERUSER_PASS',
        first_name='Admin'
    )
    print("✔ Админ создан")
else:
    print("⚠ Админ уже есть")
EOF

# 7. Наполнение данными (Seed)
# ============================================
print_step "Загрузка тестовых данных..."
python manage.py shell << 'EOF'
import sys
from apps.users.models import CustomUser
from apps.blog.models import Category, CategoryTranslation, Tag, Post, Comment

if Post.objects.exists():
    print("⏩ Данные уже есть, пропуск.")
    sys.exit(0)

# Создаем юзеров (используем preferred_language как в твоей модели)
users = []
for i in range(1, 4):
    user, _ = CustomUser.objects.get_or_create(
        username=f'user{i}',
        email=f'user{i}@test.com',
        defaults={'preferred_language': ['en', 'ru', 'kk'][i-1], 'timezone': 'Asia/Almaty'}
    )
    user.set_password('password123')
    user.save()
    users.append(user)

# Категории
cat_data = [
    {'slug': 'tech', 'ru': 'Технологии', 'kk': 'Технология', 'en': 'Tech'},
    {'slug': 'sport', 'ru': 'Спорт', 'kk': 'Спорт', 'en': 'Sport'}
]
for data in cat_data:
    c, _ = Category.objects.get_or_create(slug=data['slug'], defaults={'name': data['en']})
    for lang in ['ru', 'kk', 'en']:
        CategoryTranslation.objects.get_or_create(category=c, language=lang, name=data[lang])

# Посты (15 штук для пагинации)
for i in range(15):
    status = Post.Status.PUBLISHED if i % 2 == 0 else Post.Status.DRAFT
    Post.objects.create(
        title=f"Заголовок поста {i}",
        slug=f"post-{i}",
        body="Содержимое тестового поста " * 20,
        author=users[0],
        status=status,
        category=Category.objects.first()
    )
print("✔ База заполнена (15 постов, категории, переводы)")
EOF

# 8. Запуск
# ============================================
echo -e "${GREEN}🚀 Настройка завершена!${NC}"
echo "📄 API: http://127.0.0.1:8000/api/"
echo "📖 Docs: http://127.0.0.1:8000/api/docs/"
echo "👤 Admin: $SUPERUSER_EMAIL / $SUPERUSER_PASS"

python manage.py runserver