#include <Wire.h>
#include <LiquidCrystal_I2C.h>

#define LCD_ADDR 0x27
LiquidCrystal_I2C lcd(LCD_ADDR, 16, 2);  

String buffer;

void setup() {
  Serial.begin(115200);
  lcd.init();
  lcd.backlight();
  lcd.clear();
  lcd.setCursor(0, 0);  
  lcd.print("Waiting...");  
}

void showLines(const String& l1, const String& l2){  
  lcd.clear(); 
  lcd.setCursor(0, 0);  
  for (int i = 0; i < l1.length() && i < 16; i++) lcd.print(l1[i]);
  lcd.setCursor(0, 1);  
  for (int i = 0; i < l2.length() && i < 16; i++) lcd.print(l2[i]);
}

void loop() {
  while (Serial.available()){
    char c = (char)Serial.read();
    if (c == '\n'){
      int first = buffer.indexOf('|', 2); 
      int second = buffer.indexOf('|', first + 1);  
      if (first > 1 && second > first){
        String line1 = buffer.substring(2, first);
        String line2 = buffer.substring(first + 1, second);
        showLines(line1, line2); 
      }
      buffer = ""; 
    } else {  
      buffer += c;
      if (buffer.length() > 128) buffer = "";
    }
  }
}