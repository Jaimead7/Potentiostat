#include "Board.h"

float parseDecimal(String &str) {
  /*
  Extract decimal number from string
  */
  int charPos = str.indexOf('$');
  if (charPos == -1) {
    float number = str.toFloat();
    str = "";
    return number;
  }
  float number = str.substring(0, charPos).toFloat();
  str = str.substring(charPos);
  return number;
}
