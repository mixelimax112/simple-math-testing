@echo off
REM Быстрая загрузка проекта на AWS EC2

echo ========================================
echo   ЗАГРУЗКА ПРОЕКТА НА AWS EC2
echo ========================================
echo.

set KEY_PATH=C:\Users\mixel\.ssh\rental-housing-api.pem
set EC2_IP=98.84.179.216
set PROJECT_PATH=C:\project\rental_housing_api

echo Загружаем проект на сервер...
echo Это займет 2-3 минуты...
echo.

scp -i %KEY_PATH% -r %PROJECT_PATH% ec2-user@%EC2_IP%:/tmp/

echo.
echo ========================================
echo   ЗАГРУЗКА ЗАВЕРШЕНА!
echo ========================================
echo.
echo Теперь подключитесь к серверу:
echo   ssh -i %KEY_PATH% ec2-user@%EC2_IP%
echo.
echo И выполните на сервере:
echo   sudo mv /tmp/rental_housing_api /opt/
echo   sudo chown -R ec2-user:ec2-user /opt/rental_housing_api
echo   cd /opt/rental_housing_api
echo   bash deploy_to_aws.sh
echo.
pause
