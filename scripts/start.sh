#!/bin/bash

# Цвета для красивого вывода
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Функции-помощники
print_step() { echo -e "${BLUE}▶ $1${NC}"; }
print_success() { echo -e "${GREEN}✔ $1${NC}"; }
print_error() { echo -e "${RED}✖ $1${NC}"; }
print_warning() { echo -e "${YELLOW}⚠ $1${NC}"; }

# Проверка статуса выполнения команд
check_status() {
    if [ $? -ne 0 ]; then
        print_error "$1"
        exit 1
    fi
}

echo -e "${GREEN}"
echo "╔════════════════════════════════════════╗"
echo "║     Blog API - Automated Setup         ║"
echo "║       (Async & Redis Ready)            ║"
echo "╚════════════════════════════════════════╝"
echo -e "${NC}"

# 0. Переход в корень проекта (на уровень выше папки scripts)
cd "$(dirname "$0")/.." || exit 1

# 1. Проверка переменных среды (.env)
# ============================================
print_step "Проверка переменных окружения..."
ENV_FILE="settings/.env"

if [ ! -f "$ENV_FILE" ]; then
    print_error "Файл $ENV_FILE не найден!"
    echo "Создайте его на основе .env.example"
    exit 1
fi

# Список переменных из твоего ТЗ и кода
required_vars=("SECRET_KEY" "BLOG_DEBUG")

for var in "${required_vars[@]}"; do
    # Ищем переменную в файле, убираем пробелы
    value=$(grep "^${var}=" "$ENV_FILE" | cut -d '=' -f2- | xargs)
    if [ -z "$value" ]; then
        print_error "Переменная $var отсутствует или пуста в $ENV_FILE"
        exit 1
    fi
done
print_success "Все необходимые переменные (.env) заполнены."

# 2. Виртуальное окружение и зависимости
# ============================================
if [ ! -d "venv" ]; then
    print_step "Создание виртуального окружения..."
    python3 -m venv venv
    check_status "Не удалось создать venv"
fi

source venv/bin/activate
check_status "Не удалось активировать venv"

print_step "Установка зависимостей (включая httpx и redis)..."
pip install --upgrade pip -q
# Проверяем разные варианты расположения requirements
if [ -f "requirements.txt" ]; then
    pip install -r requirements.txt -q
elif [ -f "requirements/dev.txt" ]; then
    pip install -r requirements/dev.txt -q
fi
check_status "Ошибка при установке зависимостей"
print_success "Зависимости установлены."

# 3. База данных и Статика
# ============================================
print_step "Запуск миграций..."
python manage.py migrate --noinput
check_status "Миграции не удались"

print_step "Сбор статических файлов..."
python manage.py collectstatic --noinput -c > /dev/null
print_success "База готова, статика собрана."

# 4. Локализация
# ============================================
print_step "Компиляция файлов перевода..."
python manage.py compilemessages || print_warning "gettext не найден, пропуск компиляции."

# 5. Создание суперпользователя (Идемпотентно)
# ============================================
print_step "Проверка суперпользователя..."
ADMIN_EMAIL="admin@blog-api.com"
ADMIN_PASS="admin123"

python manage.py shell << EOF
from apps.users.models import CustomUser
if not CustomUser.objects.filter(email='$ADMIN_EMAIL').exists():
    CustomUser.objects.create_superuser(
        username='admin',
        email='$ADMIN_EMAIL',
        password='$ADMIN_PASS',
        first_name='Admin'
    )
    print("✔ Суперпользователь создан.")
else:
    print("⏩ Суперпользователь уже существует.")
EOF

# 6. Заполнение тестовыми данными (Seed)
# ============================================
print_step "Заполнение базы данными (15 постов + переводы)..."
python manage.py shell << 'EOF'
import sys
from apps.blog.models import Category, CategoryTranslation, Tag, Post, Comment
from apps.users.models import CustomUser

if Post.objects.exists():
    print("⏩ Данные уже есть, пропускаем seed.")
    sys.exit(0)

# Юзеры
users = []
for i in range(1, 4):
    u, _ = CustomUser.objects.get_or_create(
        username=f'user{i}',
        email=f'user{i}@test.com',
        defaults={'preferred_language': 'ru', 'timezone': 'Asia/Almaty'}
    )
    u.set_password('password123')
    u.save()
    users.append(u)

# Категории и их переводы
cat_data = [
    {'slug': 'tech', 'en': 'Tech', 'ru': 'Технологии', 'kk': 'Технологиялар'},
    {'slug': 'life', 'en': 'Life', 'ru': 'Жизнь', 'kk': 'Өмір'}
]
for data in cat_data:
    cat, _ = Category.objects.get_or_create(slug=data['slug'], defaults={'name': data['en']})
    for lang in ['en', 'ru', 'kk']:
        CategoryTranslation.objects.get_or_create(
            category=cat, language=lang, defaults={'name': data[lang]}
        )

# Посты (15 штук для пагинации)
for i in range(15):
    Post.objects.create(
        title=f"Тестовый пост №{i}",
        slug=f"post-{i}",
        body="Это контент для проверки асинхронной статистики и пагинации. " * 5,
        author=users[0],
        status='published',
        category=Category.objects.first()
    )
print("✔ Тестовые данные (посты, категории, переводы) успешно добавлены.")
EOF

# 7. Итог и запуск сервера
# ============================================
echo -e "${GREEN}"
echo "╔═══════════════════════════════════════════════╗"
echo "║         SETUP COMPLETE / ГОТОВО!              ║"
echo "╚═══════════════════════════════════════════════╝${NC}"
echo -e "${BLUE}Ссылки проекта:${NC}"
echo "  🚀 API Stats (Async): http://127.0.0.1:8000/api/stats/"
echo "  📖 Swagger Docs:      http://127.0.0.1:8000/api/docs/"
echo "  🔧 Admin Panel:       http://127.0.0.1:8000/admin/"
echo ""
echo -e "${BLUE}Доступы:${NC}"
echo "  Логин: $ADMIN_EMAIL / Пароль: $ADMIN_PASS"
echo ""
print_step "Запуск сервера разработки..."
python manage.py runserver