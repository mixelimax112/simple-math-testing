#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
AWS Security Group Setup Script
Автоматизирует создание и настройку Security Group для MySQL, HTTPS и SSH
"""

import boto3
import sys
import os
from datetime import datetime
from dotenv import load_dotenv

# Исправляем кодировку для Windows
if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8')

# Загружаем переменные окружения
load_dotenv()

def get_my_ip():
    """Получить текущий публичный IP адрес"""
    import requests
    try:
        response = requests.get('https://api.ipify.org?format=json', timeout=5)
        return response.json()['ip']
    except Exception as e:
        print(f"Ошибка получения IP: {e}")
        return None

def create_security_group(ec2_client, group_name, description):
    """Создать Security Group"""
    try:
        response = ec2_client.create_security_group(
            GroupName=group_name,
            Description=description
        )
        sg_id = response['GroupId']
        print(f"✓ Security Group создана: {sg_id}")
        return sg_id
    except Exception as e:
        if 'already exists' in str(e):
            print(f"Security Group '{group_name}' уже существует")
            # Получаем ID существующей группы
            response = ec2_client.describe_security_groups(
                Filters=[{'Name': 'group-name', 'Values': [group_name]}]
            )
            if response['SecurityGroups']:
                return response['SecurityGroups'][0]['GroupId']
        raise e

def add_inbound_rules(ec2_client, sg_id, my_ip):
    """Добавить inbound правила"""
    try:
        # Правило для MySQL (3306)
        ec2_client.authorize_security_group_ingress(
            GroupId=sg_id,
            IpPermissions=[
                {
                    'IpProtocol': 'tcp',
                    'FromPort': 3306,
                    'ToPort': 3306,
                    'IpRanges': [{'CidrIp': '0.0.0.0/0', 'Description': 'MySQL'}]
                }
            ]
        )
        print("✓ Правило MySQL (3306) добавлено для 0.0.0.0/0")

        # Правило для HTTPS (443)
        ec2_client.authorize_security_group_ingress(
            GroupId=sg_id,
            IpPermissions=[
                {
                    'IpProtocol': 'tcp',
                    'FromPort': 443,
                    'ToPort': 443,
                    'IpRanges': [{'CidrIp': '0.0.0.0/0', 'Description': 'HTTPS'}]
                }
            ]
        )
        print("✓ Правило HTTPS (443) добавлено для 0.0.0.0/0")

        # Правило для SSH (22) - только для вашего IP
        if my_ip:
            ec2_client.authorize_security_group_ingress(
                GroupId=sg_id,
                IpPermissions=[
                    {
                        'IpProtocol': 'tcp',
                        'FromPort': 22,
                        'ToPort': 22,
                        'IpRanges': [{'CidrIp': f'{my_ip}/32', 'Description': 'SSH My IP'}]
                    }
                ]
            )
            print(f"✓ Правило SSH (22) добавлено для {my_ip}/32")
        else:
            print("⚠ IP адрес не получен, правило SSH не добавлено")

    except Exception as e:
        if 'already exists' in str(e):
            print("⚠ Некоторые правила уже существуют")
        else:
            raise e

def describe_security_group(ec2_client, sg_id):
    """Получить информацию о Security Group"""
    response = ec2_client.describe_security_groups(
        GroupIds=[sg_id],
        Filters=[{'Name': 'group-id', 'Values': [sg_id]}]
    )
    return response['SecurityGroups'][0]

def main():
    # Проверяем наличие AWS credentials
    aws_access_key = os.getenv('AWS_ACCESS_KEY_ID')
    aws_secret_key = os.getenv('AWS_SECRET_ACCESS_KEY')
    aws_region = os.getenv('AWS_DEFAULT_REGION', 'us-east-1')

    if not aws_access_key or not aws_secret_key:
        print("❌ AWS credentials не настроены в .env файле")
        print("Добавьте в .env:")
        print("  AWS_ACCESS_KEY_ID=ваш_access_key")
        print("  AWS_SECRET_ACCESS_KEY=ваш_secret_key")
        print("  AWS_DEFAULT_REGION=регион (например us-east-1)")
        sys.exit(1)

    # Параметры
    timestamp = datetime.now().strftime('%Y%m%d')
    group_name = f"{timestamp}-andrew-sg"
    description = "Security Group for MySQL and HTTPS and SSH"

    print(f"\n{'='*60}")
    print(f"AWS Security Group Setup")
    print(f"{'='*60}\n")

    # Получаем текущий IP
    print("1. Получение текущего IP адреса...")
    my_ip = get_my_ip()
    if my_ip:
        print(f"   Ваш IP: {my_ip}")

    # Создаем EC2 клиент
    print(f"\n2. Подключение к AWS (регион: {aws_region})...")
    ec2_client = boto3.client('ec2', region_name=aws_region)

    # Создаем Security Group
    print(f"\n3. Создание Security Group '{group_name}'...")
    sg_id = create_security_group(ec2_client, group_name, description)

    # Добавляем правила
    print(f"\n4. Добавление inbound правил...")
    add_inbound_rules(ec2_client, sg_id, my_ip)

    # Получаем полную информацию
    print(f"\n5. Получение информации о Security Group...")
    sg_info = describe_security_group(ec2_client, sg_id)

    # Выводим результат
    print(f"\n{'='*60}")
    print(f"РЕЗУЛЬТАТ")
    print(f"{'='*60}")
    print(f"\nSecurity Group ID: {sg_id}")
    print(f"Group Name: {sg_info['GroupName']}")
    print(f"Description: {sg_info['Description']}")
    print(f"VPC ID: {sg_info['VpcId']}")

    print(f"\nInbound правила:")
    for rule in sg_info['IpPermissions']:
        port = rule.get('FromPort', 'N/A')
        protocol = rule.get('IpProtocol', 'N/A')
        ip_ranges = rule.get('IpRanges', [])
        for ip_range in ip_ranges:
            cidr = ip_range.get('CidrIp', 'N/A')
            desc = ip_range.get('Description', '')
            print(f"  - Port {port}/{protocol}: {cidr} ({desc})")

    print(f"\n{'='*60}")
    print("\n✅ Настройка завершена!")
    print(f"\nКоманда для проверки:")
    print(f"aws ec2 describe-security-groups --group-ids {sg_id} --query 'SecurityGroups[*].IpPermissions' --output json")
    print(f"\n{'='*60}\n")

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"\n❌ Ошибка: {e}")
        sys.exit(1)
