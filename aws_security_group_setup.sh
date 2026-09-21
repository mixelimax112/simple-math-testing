#!/bin/bash

# AWS Security Group Setup Script
# Выполните этот скрипт после установки AWS CLI и настройки credentials

# Переменные (замените на ваши значения)
YOUR_NAME="andrew"
YOUR_GROUP_NAME="2024091S"
YOUR_IP=$(curl -s https://api.ipify.org)  # Автоматически получит ваш IP

echo "=== Задание 1: Создание Security Group ==="
SG_ID=$(aws ec2 create-security-group \
    --group-name "${YOUR_NAME}-${YOUR_GROUP_NAME}-sg" \
    --description "Security Group for MySQL and HTTPS and SSH" \
    --query 'GroupId' \
    --output text)

echo "Создана Security Group с ID: $SG_ID"
echo ""

echo "=== Задание 2: Добавление правил входящего трафика ==="
# Правило для MySQL (порт 3306)
aws ec2 authorize-security-group-ingress \
    --group-id $SG_ID \
    --ip-permissions IpProtocol=tcp,FromPort=3306,ToPort=3306,IpRanges='[{CidrIp=0.0.0.0/0,Description="mysql"}]'

echo "Добавлено правило для MySQL (порт 3306)"

# Правило для HTTPS (порт 443)
aws ec2 authorize-security-group-ingress \
    --group-id $SG_ID \
    --ip-permissions IpProtocol=tcp,FromPort=443,ToPort=443,IpRanges='[{CidrIp=0.0.0.0/0,Description="https"}]'

echo "Добавлено правило для HTTPS (порт 443)"
echo ""

echo "=== Задание 3: Добавление правила SSH для вашего IP ==="
# Правило для SSH (порт 22) только для вашего IP
aws ec2 authorize-security-group-ingress \
    --group-id $SG_ID \
    --ip-permissions IpProtocol=tcp,FromPort=22,ToPort=22,IpRanges="[{CidrIp=${YOUR_IP}/32,Description=\"SSH My IP\"}]"

echo "Добавлено правило для SSH (порт 22) для IP: ${YOUR_IP}/32"
echo ""

echo "=== Задание 4: Вывод информации о Security Group ==="
aws ec2 describe-security-groups \
    --group-ids $SG_ID \
    --query 'SecurityGroups[*].IpPermissions' \
    --output json

echo ""
echo "=== Задание 5: Команды, использованные для создания ==="
echo "1. aws ec2 create-security-group --group-name \"${YOUR_NAME}-${YOUR_GROUP_NAME}-sg\" --description \"Security Group for MySQL and HTTPS and SSH\""
echo "2. aws ec2 authorize-security-group-ingress --group-id $SG_ID --ip-permissions IpProtocol=tcp,FromPort=3306,ToPort=3306,IpRanges='[{CidrIp=0.0.0.0/0,Description=\"mysql\"}]'"
echo "3. aws ec2 authorize-security-group-ingress --group-id $SG_ID --ip-permissions IpProtocol=tcp,FromPort=443,ToPort=443,IpRanges='[{CidrIp=0.0.0.0/0,Description=\"https\"}]'"
echo "4. aws ec2 authorize-security-group-ingress --group-id $SG_ID --ip-permissions IpProtocol=tcp,FromPort=22,ToPort=22,IpRanges=\"[{CidrIp=${YOUR_IP}/32,Description=\\\"SSH My IP\\\"}]\""
echo ""

echo "=== Задание 6: Удаление Security Group ==="
echo "Чтобы удалить Security Group, выполните:"
echo "aws ec2 delete-security-group --group-id $SG_ID"
echo ""
echo "ID вашей Security Group: $SG_ID"
echo "Сохраните его для дальнейшего использования!"
