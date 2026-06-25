# Установка geckodriver для Firefox

## Что такое geckodriver?

Geckodriver - это WebDriver для Firefox, необходимый для автоматизации браузера с помощью Selenium.

## Установка

### Автоматическая установка (рекомендуется)

Используйте webdriver-manager для автоматической установки:

```bash
pip install webdriver-manager
```

Затем обновите скрипт для использования webdriver-manager (пример в коде ниже).

### Ручная установка

#### Windows:

1. Перейдите на https://github.com/mozilla/geckodriver/releases
2. Скачайте `geckodriver-vX.XX.X-win64.zip` (последняя версия)
3. Распакуйте архив
4. Скопируйте `geckodriver.exe` в одну из папок:
   - `C:\Windows\` (требуются права администратора)
   - Или в любую папку и добавьте её в PATH

**Добавление в PATH:**
1. Откройте "Панель управления" → "Система" → "Дополнительные параметры системы"
2. Нажмите "Переменные среды"
3. В разделе "Системные переменные" найдите `Path` и нажмите "Изменить"
4. Добавьте путь к папке с geckodriver.exe

#### Linux:

```bash
# Скачайте последнюю версию
wget https://github.com/mozilla/geckodriver/releases/download/v0.34.0/geckodriver-v0.34.0-linux64.tar.gz

# Распакуйте
tar -xvzf geckodriver-v0.34.0-linux64.tar.gz

# Переместите в системную папку
sudo mv geckodriver /usr/local/bin/

# Дайте права на выполнение
sudo chmod +x /usr/local/bin/geckodriver
```

#### macOS:

```bash
# Через Homebrew (проще всего)
brew install geckodriver

# Или вручную
wget https://github.com/mozilla/geckodriver/releases/download/v0.34.0/geckodriver-v0.34.0-macos.tar.gz
tar -xvzf geckodriver-v0.34.0-macos.tar.gz
sudo mv geckodriver /usr/local/bin/
```

## Проверка установки

```bash
geckodriver --version
```

Если команда выводит версию - установка прошла успешно.

## Использование в Python

### С автоматической установкой (webdriver-manager):

```python
from selenium import webdriver
from selenium.webdriver.firefox.service import Service
from webdriver_manager.firefox import GeckoDriverManager

# Автоматически скачает и настроит geckodriver
driver = webdriver.Firefox(service=Service(GeckoDriverManager().install()))
```

### С ручной установкой:

```python
from selenium import webdriver

# Если geckodriver в PATH
driver = webdriver.Firefox()

# Или укажите путь явно
from selenium.webdriver.firefox.service import Service
service = Service(executable_path='C:/path/to/geckodriver.exe')
driver = webdriver.Firefox(service=service)
```

## Требования

- Firefox браузер должен быть установлен
- Python 3.7+
- Selenium 4.x

```bash
pip install selenium webdriver-manager
```

## Запуск screenshot_script.py

После установки geckodriver:

```bash
python screenshot_script.py
```

Скрипт откроет Firefox, перейдёт на itcareerhub.de и сделает скриншот раздела "Способы оплаты".
