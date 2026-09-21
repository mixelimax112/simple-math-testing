# Инструкция по выполнению задания AWS Security Groups

## Шаг 1: Установка AWS CLI

### Для Windows:
1. Скачайте установщик: https://awscli.amazonaws.com/AWSCLIV2.msi
2. Запустите установщик
3. Перезапустите терминал

### Проверка установки:
```bash
aws --version
```

## Шаг 2: Настройка AWS credentials

```bash
aws configure
```

Вам нужно будет ввести:
- AWS Access Key ID
- AWS Secret Access Key
- Default region name (например: us-east-1)
- Default output format (json)

## Шаг 3: Выполнение заданий

### Задание 1: Создание Security Group

```bash
aws ec2 create-security-group \
    --group-name "andrew-20240915-sg" \
    --description "Security Group for MySQL and HTTPS and SSH"
```

Сохраните полученный `GroupId` (например: `sg-092d4ec2208cc14a6`)

### Задание 2: Добавление правил для портов 3306 и 443

**Правило для MySQL (порт 3306):**
```bash
aws ec2 authorize-security-group-ingress \
    --group-id sg-092d4ec2208cc14a6 \
    --ip-permissions IpProtocol=tcp,FromPort=3306,ToPort=3306,IpRanges='[{CidrIp=0.0.0.0/0,Description="mysql"}]'
```

**Правило для HTTPS (порт 443):**
```bash
aws ec2 authorize-security-group-ingress \
    --group-id sg-092d4ec2208cc14a6 \
    --ip-permissions IpProtocol=tcp,FromPort=443,ToPort=443,IpRanges='[{CidrIp=0.0.0.0/0,Description="https"}]'
```

### Задание 3: Добавление правила SSH (порт 22) для вашего IP

**Узнайте свой IP-адрес:**
```bash
curl https://api.ipify.org
```

**Добавьте правило (замените YOUR_IP на ваш реальный IP):**
```bash
aws ec2 authorize-security-group-ingress \
    --group-id sg-092d4ec2208cc14a6 \
    --ip-permissions IpProtocol=tcp,FromPort=22,ToPort=22,IpRanges='[{CidrIp=YOUR_IP/32,Description="SSH My IP"}]'
```

Пример:
```bash
aws ec2 authorize-security-group-ingress \
    --group-id sg-092d4ec2208cc14a6 \
    --ip-permissions IpProtocol=tcp,FromPort=22,ToPort=22,IpRanges='[{CidrIp=203.0.113.25/32,Description="SSH My IP"}]'
```

### Задание 4: Просмотр правил Security Group

```bash
aws ec2 describe-security-groups \
    --group-ids sg-092d4ec2208cc14a6 \
    --query 'SecurityGroups[*].IpPermissions' \
    --output json
```

### Задание 5: Список всех использованных команд

1. Создание Security Group:
```bash
aws ec2 create-security-group --group-name "andrew-20240915-sg" --description "Security Group for MySQL and HTTPS and SSH"
```

2. Добавление правила для MySQL:
```bash
aws ec2 authorize-security-group-ingress --group-id sg-092d4ec2208cc14a6 --ip-permissions IpProtocol=tcp,FromPort=3306,ToPort=3306,IpRanges='[{CidrIp=0.0.0.0/0,Description="mysql"}]'
```

3. Добавление правила для HTTPS:
```bash
aws ec2 authorize-security-group-ingress --group-id sg-092d4ec2208cc14a6 --ip-permissions IpProtocol=tcp,FromPort=443,ToPort=443,IpRanges='[{CidrIp=0.0.0.0/0,Description="https"}]'
```

4. Добавление правила для SSH:
```bash
aws ec2 authorize-security-group-ingress --group-id sg-092d4ec2208cc14a6 --ip-permissions IpProtocol=tcp,FromPort=22,ToPort=22,IpRanges='[{CidrIp=YOUR_IP/32,Description="SSH My IP"}]'
```

### Задание 6: Удаление Security Group

```bash
aws ec2 delete-security-group --group-id sg-092d4ec2208cc14a6
```

## Альтернатива: Автоматический скрипт

Вы можете использовать готовый скрипт `aws_security_group_setup.sh`:

1. Отредактируйте переменные в начале скрипта (ваше имя и группу)
2. Выполните:
```bash
bash aws_security_group_setup.sh
```

## Важные замечания

- **Замените `sg-092d4ec2208cc14a6`** на ID вашей реальной Security Group
- **Замените `YOUR_IP`** на ваш реальный IP-адрес
- **Замените имя группы** если у вас другие данные
- **0.0.0.0/0** означает доступ отовсюду (для MySQL и HTTPS)
- **/32** в конце IP означает только один конкретный IP-адрес (для SSH)

## Проверка в AWS Console

После выполнения команд можете проверить результат в AWS Management Console:
1. Зайдите в EC2 → Security Groups
2. Найдите вашу Security Group
3. Проверьте вкладки "Inbound rules" и "Outbound rules"
