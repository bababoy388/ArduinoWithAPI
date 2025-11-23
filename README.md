<h1>Уведомления о новых видео YouTube на LCD 16×2 через Arduino Uno и FastAPI</h1>

Описание

ПК опрашивает RSS-ленту YouTube каналов (без API‑ключа).
При появлении нового видео сервер отправляет сообщение по USB‑Serial на Arduino Uno.
Arduino выводит на LCD 16×2 короткий текст: название канала и заголовок видео.

Особенности

Без ключей: используется RSS https://www.youtube.com/feeds/videos.xml?channel_id=<CHANNEL_ID>
Простой протокол по Serial: L|<line1>|<line2>\n
Транслитерация (Unidecode) и обрезка строк до 16 символов для LCD.
FastAPI с фоновым воркером, эндпоинты для просмотра/добавления каналов.

Аппаратные требования

Arduino Uno.
LCD 16×2 с I2C-платкой (PCF8574).

Структура проекта.

main.py
app/
utils.py
endpoints.py
settings.py
models.py
sketch/
sketch_nov20a.ino

Arduino: скетч для LCD и парсинга сообщений

```
#include <Wire.h>
#include <LiquidCrystal_I2C.h>

#define LCD_ADDR 0x27
LiquidCrystal_I2C lcd(LCD_ADDR, 16, 2);

String buffer;

void printLine(uint8_t row, const String& s) {
  lcd.setCursor(0, row);
  for (int i = 0; i < 16; i++) {
    char c = (i < (int)s.length()) ? s[i] : ' ';
    lcd.print(c);
  }
}

void showLines(const String& l1, const String& l2) {
  printLine(0, l1);
  printLine(1, l2);
}

void setup() {
  Serial.begin(115200);
  lcd.init();
  lcd.backlight();
  lcd.clear();
  lcd.setCursor(0, 0);
  lcd.print("Waiting...");
  // Для отладки можно послать хэндшейк:
  // Serial.println("READY");
}

void loop() {
  while (Serial.available()) {
    char c = (char)Serial.read();
    if (c == '\n') {
      if (buffer.length() > 0 && buffer[buffer.length() - 1] == '\r') {
        buffer.remove(buffer.length() - 1);
      }
      // ожидаем формат: L|<line1>|<line2>
      if (buffer.startsWith("L|")) {
        int sep = buffer.indexOf('|', 2); // разделитель между line1 и line2
        if (sep > 1) {
          String line1 = buffer.substring(2, sep);
          String line2 = buffer.substring(sep + 1); // до конца
          showLines(line1, line2);
        }
      }
      buffer = "";
    } else {
      buffer += c;
      if (buffer.length() > 128) buffer = "";
    }
  }
}
```
Сервер: требования и установка

Python 3.10+
Зависимости:
fastapi
uvicorn[standard]
httpx
pyserial
feedparser
Unidecode
pydantic (версия 2+; используется модуль pydantic.v1)
Установка зависимостей:

```
pip install fastapi "uvicorn[standard]" httpx pyserial feedparser Unidecode "pydantic>=2"
```
Настройки через переменные окружения

SERIAL_PORT — порт Arduino (например, COM3, /dev/ttyACM0, /dev/cu.usbmodemXXX).
BAUDRATE — скорость порта (по умолчанию 115200).
POLL_SECONDS — период опроса RSS (по умолчанию 60).
CHANNEL_IDS — список channel_id через запятую (например, UC_xxx,UC_yyy).

Запуск сервера

```
python main.py
```
# или
```
uvicorn main:app --host 0.0.0.0 --port 8000
```

Формат: L|<line1>|<line2>\n
Ограничения:
Чёрточки ‘|’ заранее меняются на ‘/’.
Строки транслитерируются в ASCII (Unidecode) и обрезаются до 16 символов.
Пример полезной нагрузки: L|Channel Name|New video title\n

Как найти channel_id на YouTube

Если ссылка вида https://www.youtube.com/channel/UCxxxx — используйте UCxxxx.
Если ссылка вида https://www.youtube.com/@handle — откройте страницу канала и поищите “ID канала” на вкладке “О канале”, либо используйте онлайн‑конвертер handle → channel_id.
RSS URL: https://www.youtube.com/feeds/videos.xml?channel_id=CHANNEL_ID
