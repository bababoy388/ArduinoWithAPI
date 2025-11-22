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
  // без полного clear — меньше мерцания
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
      // удалить возможный '\r'
      if (buffer.length() > 0 && buffer[buffer.length() - 1] == '\r') {
        buffer.remove(buffer.length() - 1);
      }
      // ожидаем: L|<line1>|<line2>
      if (buffer.startsWith("L|")) {
        int sep = buffer.indexOf('|', 2); // разделитель между line1 и line2
        if (sep > 1) {
          String line1 = buffer.substring(2, sep);
          String line2 = buffer.substring(sep + 1); // до конца
          showLines(line1, line2);
        }
      }
      buffer = ""; // сброс
    } else {
      buffer += c;
      if (buffer.length() > 128) buffer = ""; // защита
    }
  }
}
