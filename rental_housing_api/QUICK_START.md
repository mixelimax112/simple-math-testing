# 🚀 БЫСТРЫЙ ДЕПЛОЙ НА AWS EC2

## Вариант 1: Автоматический деплой (РЕКОМЕНДУЕТСЯ)

### В PowerShell на вашем компьютере:

```powershell
# 1. Загрузите весь проект на сервер
cd C:\project
scp -i C:\Users\mixel\.ssh\rental-housing-api.pem -r rental_housing_api ec2-user@98.84.179.216:/home/ec2-user/

# 2. Подключитесь к серверу
ssh -i C:\Users\mixel\.ssh\rental-housing-api.pem ec2-user@98.84.179.216
```

### На сервере (в SSH):

```bash
# 3. Переместите проект
sudo mv /home/ec2-user/rental_housing_api /opt/
sudo chown -R ec2-user:ec2-user /opt/rental_housing_api
cd /opt/rental_housing_api

# 4. Запустите автоматическую установку
bash deploy_to_aws.sh

# 5. ВАЖНО: Выйдите и войдите снова для применения прав
exit
```

```powershell
# 6. Подключитесь снова
ssh -i C:\Users\mixel\.ssh\rental-housing-api.pem ec2-user@98.84.179.216
```

```bash
# 7. Запустите приложение
cd /opt/rental_housing_api
docker-compose up -d --build

# 8. Дождитесь запуска (30-60 секунд), затем создайте админа
docker-compose exec web python manage.py createsuperuser
```

### Готово! Откройте в браузере:
- **API**: http://98.84.179.216:8000/api/
- **Документация**: http://98.84.179.216:8000/api/docs/
- **Админка**: http://98.84.179.216:8000/admin/

---

## Вариант 2: Через Git (если проект в GitHub)

```bash
# На сервере
cd /opt
sudo git clone https://github.com/YOUR_USERNAME/rental_housing_api.git
sudo chown -R ec2-user:ec2-user rental_housing_api
cd rental_housing_api

# Далее выполните шаги 4-8 из Варианта 1
```

---

## 🛠️ Полезные команды

```bash
# Посмотреть логи
docker-compose logs -f

# Перезапустить
docker-compose restart

# Остановить
docker-compose down

# Запустить заново
docker-compose up -d

# Проверить статус
docker-compose ps
```

---

## ⚠️ Если что-то пошло не так

```bash
# Полная очистка и перезапуск
cd /opt/rental_housing_api
docker-compose down -v
docker system prune -af
docker-compose up -d --build

# Посмотреть, что не так
docker-compose logs web
docker-compose logs db
```

---

## 📝 Важно перед запуском

В файле `.env` (уже создан) проверьте:
- `SECRET_KEY` - смените на случайную строку 50+ символов
- `ALLOWED_HOSTS` - добавьте ваш домен, если есть

```bash
nano /opt/rental_housing_api/.env
```

---

## 🎯 Быстрый чеклист

- [ ] Файлы загружены на сервер
- [ ] `deploy_to_aws.sh` выполнен
- [ ] Выход/вход для прав Docker
- [ ] `docker-compose up -d --build` запущен
- [ ] Суперпользователь создан
- [ ] API открывается в браузере

**Время деплоя: ~10 минут** ⚡
