# 🚀 Деплой Rental Housing API на AWS EC2

Полная инструкция по развертыванию Django REST API проекта на Amazon EC2.

---

## 📋 Подготовка

### Что вам понадобится:
- AWS аккаунт
- Доменное имя (опционально, для SSL)
- SSH клиент

---

## 1️⃣ Создание EC2 Instance

### Шаг 1: Запуск инстанса
1. Войдите в [AWS Console](https://console.aws.amazon.com/)
2. Перейдите в **EC2 Dashboard**
3. Нажмите **Launch Instance**

### Шаг 2: Настройка инстанса
- **Name**: `rental-housing-api`
- **AMI**: Ubuntu Server 22.04 LTS (free tier eligible)
- **Instance type**: `t2.micro` (для начала) или `t2.small` (рекомендуется)
- **Key pair**: Создайте новую или используйте существующую
  - Сохраните `.pem` файл в безопасное место!

### Шаг 3: Network settings (Security Group)
Создайте security group со следующими правилами:

| Type | Protocol | Port Range | Source | Description |
|------|----------|------------|--------|-------------|
| SSH | TCP | 22 | My IP | SSH access |
| HTTP | TCP | 80 | 0.0.0.0/0 | HTTP access |
| HTTPS | TCP | 443 | 0.0.0.0/0 | HTTPS access |

### Шаг 4: Storage
- Минимум: 20 GB
- Рекомендуется: 30 GB для production

### Шаг 5: Launch Instance
Нажмите **Launch Instance** и дождитесь запуска.

---

## 2️⃣ Подключение к серверу

### Получите IP адрес:
В EC2 Dashboard найдите ваш instance и скопируйте **Public IPv4 address**

### Подключитесь через SSH:

**Linux/Mac:**
```bash
chmod 400 your-key.pem
ssh -i your-key.pem ubuntu@YOUR_EC2_IP
```

**Windows (PowerShell):**
```powershell
ssh -i your-key.pem ubuntu@YOUR_EC2_IP
```

---

## 3️⃣ Настройка сервера

### Загрузите проект на сервер:

**Вариант А: Через Git (рекомендуется)**
```bash
# Сначала запушьте проект в GitHub/GitLab

# На сервере:
cd /opt
sudo mkdir rental_housing_api
sudo chown ubuntu:ubuntu rental_housing_api
git clone https://github.com/YOUR_USERNAME/rental_housing_api.git rental_housing_api
cd rental_housing_api
```

**Вариант Б: Через SCP (прямая загрузка)**
```bash
# С вашего компьютера:
scp -i your-key.pem -r C:\project\rental_housing_api ubuntu@YOUR_EC2_IP:/tmp/

# На сервере:
sudo mv /tmp/rental_housing_api /opt/
sudo chown -R ubuntu:ubuntu /opt/rental_housing_api
```

### Запустите скрипт настройки:
```bash
cd /opt/rental_housing_api
bash deploy/setup_ec2.sh
```

⚠️ **После установки выйдите и войдите снова:**
```bash
exit
ssh -i your-key.pem ubuntu@YOUR_EC2_IP
```

---

## 4️⃣ Конфигурация приложения

### Создайте .env файл:
```bash
cd /opt/rental_housing_api
cp .env.production .env
nano .env
```

### Настройте переменные окружения:

```env
DEBUG=False
SECRET_KEY=ваш-секретный-ключ-минимум-50-символов
ALLOWED_HOSTS=ваш-домен.com,YOUR_EC2_IP

USE_MYSQL=True
DB_NAME=rental_housing
DB_USER=rental_user
DB_PASSWORD=надежный-пароль-для-БД
DB_HOST=db
DB_PORT=3306

CORS_ALLOWED_ORIGINS=https://ваш-фронтенд.com
```

### Генерация SECRET_KEY:
```bash
python3 -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
```

**Сохраните файл:** `Ctrl+X` → `Y` → `Enter`

---

## 5️⃣ Деплой приложения

### Запустите деплой:
```bash
cd /opt/rental_housing_api
bash deploy/deploy.sh
```

### Создайте суперпользователя:
```bash
docker-compose -f docker-compose.prod.yml exec web python manage.py createsuperuser
```

Введите:
- Email
- Password
- Role: выберите `landlord` или `tenant`

---

## 6️⃣ Проверка работы

### Откройте браузер и перейдите:
- **API Root**: `http://YOUR_EC2_IP/api/`
- **Admin Panel**: `http://YOUR_EC2_IP/admin/`
- **API Docs**: `http://YOUR_EC2_IP/api/docs/`

### Проверьте статус контейнеров:
```bash
docker-compose -f /opt/rental_housing_api/docker-compose.prod.yml ps
```

Все три контейнера должны быть в статусе `Up`:
- `rental_mysql_prod`
- `rental_web_prod`
- `rental_nginx`

---

## 7️⃣ Настройка домена (опционально)

### Если у вас есть домен:

1. **Добавьте A-запись** в DNS провайдере:
   ```
   Type: A
   Name: api (или @)
   Value: YOUR_EC2_IP
   TTL: 300
   ```

2. **Обновите .env**:
   ```bash
   nano /opt/rental_housing_api/.env
   ```
   Измените `ALLOWED_HOSTS=api.ваш-домен.com`

3. **Настройте SSL с Let's Encrypt**:
   ```bash
   sudo certbot --nginx -d api.ваш-домен.com
   ```

4. **Перезапустите nginx**:
   ```bash
   docker-compose -f /opt/rental_housing_api/docker-compose.prod.yml restart nginx
   ```

---

## 🛠️ Полезные команды

### Просмотр логов:
```bash
# Все сервисы
docker-compose -f /opt/rental_housing_api/docker-compose.prod.yml logs -f

# Только web
docker-compose -f /opt/rental_housing_api/docker-compose.prod.yml logs -f web

# Только база данных
docker-compose -f /opt/rental_housing_api/docker-compose.prod.yml logs -f db
```

### Перезапуск сервисов:
```bash
cd /opt/rental_housing_api

# Перезапуск всех контейнеров
docker-compose -f docker-compose.prod.yml restart

# Перезапуск только web
docker-compose -f docker-compose.prod.yml restart web
```

### Остановка сервисов:
```bash
docker-compose -f /opt/rental_housing_api/docker-compose.prod.yml down
```

### Запуск после остановки:
```bash
docker-compose -f /opt/rental_housing_api/docker-compose.prod.yml up -d
```

### Обновление кода (если используете Git):
```bash
cd /opt/rental_housing_api
git pull origin main
bash deploy/deploy.sh
```

### Резервное копирование БД:
```bash
bash /opt/rental_housing_api/deploy/backup_db.sh
```

Бэкапы сохраняются в `/opt/rental_housing_api/backups/`

### Восстановление из бэкапа:
```bash
gunzip backup_file.sql.gz
docker-compose -f docker-compose.prod.yml exec -T db mysql -u rental_user -p rental_housing < backup_file.sql
```

---

## 🔒 Безопасность

### ✅ Обязательно сделайте:

1. **Смените пароли по умолчанию**
   - SECRET_KEY
   - DB_PASSWORD
   - Пароль суперпользователя

2. **Настройте firewall** (скрипт делает это автоматически)
   ```bash
   sudo ufw status
   ```

3. **Регулярно обновляйте систему**
   ```bash
   sudo apt-get update && sudo apt-get upgrade -y
   ```

4. **Настройте автоматические бэкапы** (добавьте в cron)
   ```bash
   crontab -e
   # Добавьте строку:
   0 2 * * * /opt/rental_housing_api/deploy/backup_db.sh
   ```

5. **Используйте SSL/HTTPS** в продакшене

---

## 📊 Мониторинг

### Проверка использования ресурсов:
```bash
# CPU и память
docker stats

# Диск
df -h

# Системные ресурсы
htop
```

### Health check endpoint:
```bash
curl http://YOUR_EC2_IP/health
# Должен вернуть: healthy
```

---

## 🐛 Troubleshooting

### Проблема: Контейнер web не запускается

**Решение:**
```bash
# Проверьте логи
docker-compose -f docker-compose.prod.yml logs web

# Проверьте .env файл
cat /opt/rental_housing_api/.env

# Пересоберите контейнер
docker-compose -f docker-compose.prod.yml up -d --build web
```

### Проблема: Не могу подключиться к API

**Решение:**
```bash
# Проверьте, что контейнеры запущены
docker ps

# Проверьте Security Group в AWS
# Должны быть открыты порты 80 и 443

# Проверьте nginx
docker-compose -f docker-compose.prod.yml logs nginx
```

### Проблема: Ошибка подключения к БД

**Решение:**
```bash
# Проверьте MySQL контейнер
docker-compose -f docker-compose.prod.yml logs db

# Проверьте переменные окружения
docker-compose -f docker-compose.prod.yml exec web env | grep DB

# Перезапустите БД
docker-compose -f docker-compose.prod.yml restart db
```

---

## 💰 Стоимость

### Примерная стоимость на AWS:

- **t2.micro** (1 vCPU, 1 GB RAM): ~$8/месяц
- **t2.small** (1 vCPU, 2 GB RAM): ~$17/месяц
- **t2.medium** (2 vCPU, 4 GB RAM): ~$34/месяц

**+ хранилище**: ~$2-3/месяц за 30 GB  
**+ трафик**: первые 100 GB бесплатно

💡 **Free Tier**: первые 12 месяцев можно использовать t2.micro бесплатно (750 часов/месяц)

---

## 📞 Поддержка

Если возникли проблемы:
1. Проверьте логи: `docker-compose logs -f`
2. Проверьте статус: `docker-compose ps`
3. Проверьте .env файл
4. Проверьте Security Group в AWS

---

## ✅ Checklist деплоя

- [ ] EC2 instance создан и запущен
- [ ] Security Group настроен (порты 22, 80, 443)
- [ ] SSH подключение работает
- [ ] Docker и Docker Compose установлены
- [ ] Проект загружен на сервер
- [ ] .env файл создан и настроен
- [ ] Приложение задеплоено
- [ ] Контейнеры запущены
- [ ] Суперпользователь создан
- [ ] API доступен через браузер
- [ ] Настроен домен (опционально)
- [ ] SSL сертификат установлен (опционально)
- [ ] Автоматические бэкапы настроены

---

**🎉 Поздравляю! Ваш API успешно задеплоен на AWS!**
