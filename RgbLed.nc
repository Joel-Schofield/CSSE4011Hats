// this is for csse4011

interface RgbLed {

  command void setColorRgb(uint8_t red, uint8_t green, uint8_t blue);  
  command void setMultRgb(uint8_t* red, uint8_t* green, uint8_t* blue, uint8_t len);  
}
