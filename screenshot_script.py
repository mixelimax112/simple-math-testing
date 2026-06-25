from selenium import webdriver
from selenium.webdriver.firefox.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time


def take_screenshot():
    """Открывает Firefox, переходит в раздел 'Способы оплаты' и делает скриншот."""

    # Инициализация Firefox драйвера
    driver = webdriver.Firefox()

    try:
        # Открываем страницу
        driver.get("https://itcareerhub.de/ru")

        # Ожидаем загрузки страницы
        time.sleep(3)

        # Ищем и кликаем на раздел "Способы оплаты"
        # Можно использовать разные стратегии поиска элемента
        try:
            # Пытаемся найти ссылку по тексту
            payment_link = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.LINK_TEXT, "Способы оплаты"))
            )
            payment_link.click()
        except:
            # Альтернативный поиск по частичному тексту
            try:
                payment_link = driver.find_element(By.PARTIAL_LINK_TEXT, "оплат")
                payment_link.click()
            except:
                print("Не удалось найти раздел 'Способы оплаты'")
                print("Попробуем найти через навигацию...")
                # Можно добавить дополнительную логику поиска

        # Ждем загрузки страницы с способами оплаты
        time.sleep(3)

        # Делаем скриншот
        screenshot_path = "payment_methods_screenshot.png"
        driver.save_screenshot(screenshot_path)
        print(f"Скриншот сохранён: {screenshot_path}")

    except Exception as e:
        print(f"Произошла ошибка: {e}")
        # Делаем скриншот для отладки
        driver.save_screenshot("error_screenshot.png")

    finally:
        # Закрываем браузер
        driver.quit()


if __name__ == "__main__":
    take_screenshot()
