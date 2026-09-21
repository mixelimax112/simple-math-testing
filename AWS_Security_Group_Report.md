# AWS Security Group - Лабораторная работа

**Дата:** 30.07.2026  
**Студент:** Maksym Kravchenko  
**Группа:** 121225-PTM

---

## Задание

Создать Security Group для AWS EC2 с правилами доступа для MySQL, HTTPS и SSH.

---

## Выполнение

### 1. Создание Security Group

Создал новую Security Group с помощью AWS CLI:

```bash
aws ec2 create-security-group \
  --group-name 20260730-maksym-kravchenko-121225ptm-sg \
  --description "Security Group for MySQL and HTTPS and SSH"
```

Получил ID: `sg-00f7ea92647f689b2`

### 2. Настройка правил входящего трафика

Добавил три правила для входящего трафика:

**MySQL (порт 3306):**
```bash
aws ec2 authorize-security-group-ingress \
  --group-id sg-00f7ea92647f689b2 \
  --protocol tcp \
  --port 3306 \
  --cidr 0.0.0.0/0
```

**HTTPS (порт 443):**
```bash
aws ec2 authorize-security-group-ingress \
  --group-id sg-00f7ea92647f689b2 \
  --protocol tcp \
  --port 443 \
  --cidr 0.0.0.0/0
```

**SSH (порт 22):**
```bash
aws ec2 authorize-security-group-ingress \
  --group-id sg-00f7ea92647f689b2 \
  --protocol tcp \
  --port 22 \
  --cidr 109.41.240.21/32
```

### 3. Проверка настроек

Проверил созданную Security Group:

```bash
aws ec2 describe-security-groups --group-ids sg-00f7ea92647f689b2
```

---

## Результаты

**Security Group ID:** sg-00f7ea92647f689b2  
**Имя:** 20260730-maksym-kravchenko-121225ptm-sg  
**VPC:** vpc-0a02936a83dd85c84  
**Регион:** us-east-1  
**Мой IP адрес:** 109.41.240.21

### Таблица правил

| Порт | Протокол | Источник | Назначение |
|------|----------|----------|------------|
| 22   | TCP      | 109.41.240.21/32 | SSH доступ |
| 3306 | TCP      | 0.0.0.0/0 | MySQL database |
| 443  | TCP      | 0.0.0.0/0 | HTTPS трафик |

---

## Выводы

В ходе выполнения лабораторной работы:
- Изучил работу с AWS CLI для управления Security Groups
- Настроил правила firewall для различных сервисов
- Применил принцип минимальных привилегий (SSH доступен только с моего IP)
- Проверил корректность настроек через describe-security-groups

Все задачи выполнены успешно.
