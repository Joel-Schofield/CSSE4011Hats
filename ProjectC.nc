// this is for csse4011 


#include "printf.h"

module BlinkTimeSyncC
{
  uses {
    interface Boot;
    interface Leds;
    interface RgbLed;
    
    interface Timer<TMilli> as BlinkTimer;

    interface SplitControl as RadioControl;
    interface StdControl as TimeSyncControl;
    interface LocalTime<TMilli>;
    interface GlobalTime<TMilli>;
  }
}

implementation
{

  // globals
  uint32_t out = 0;
  uint32_t ledVal = 0;
  uint32_t refLocalTime = 0;
  uint32_t refGlobalTime = 0;

  event void Boot.booted() {

    printf("Booted\n");
    printfflush();

    // start radio
    call RadioControl.start();

    // switch off all Leds
    call Leds.set(0);
    call RgbLed.setColorRgb(0, 0, 0);

    // start timer to toggle LEDs
    call BlinkTimer.startPeriodic(100);
  }
  
  event void RadioControl.startDone(error_t error) {
  
    // start timesync service
    call TimeSyncControl.start();
  }


  event void BlinkTimer.fired() {

    uint32_t localTime;

    // if Globaltime get is successfull then update the globaltime reference
    if (call GlobalTime.getGlobalTime(&refGlobalTime) == SUCCESS) {
      // update the local time reference with the latest global agreed time
      refLocalTime = call LocalTime.get();
      // print success
      printf("GlobalTime get successfull, refLocalTime: %lu\r\n", refGlobalTime);
    }
    // if it fails, do not update the globaltime ref, or the localtime
    else {
      printf("GlobalTime get unsuccessfull\r\n");
    }
    printfflush();

    // store the local time in a varable used for calculations
    localTime = call LocalTime.get();

    // when the motes are synct the localtime - reflocal time will be 0, and the
    // refglobal will be equal. meaning that out will be the same number
    // on both motes
    out = (((refGlobalTime + (localTime - refLocalTime )) >> 10) % 7);
    
    // set the leds according to the out patten
    call Leds.set(out);

    // set a random colour (RGB) from the results of out
    // 255 is max, so if outs bits match 4, then put maximum brightness onto 
    // red if match 2 max onto green 1, max onto blue
    call RgbLed.setColorRgb(((out & 4) * 255), ((out & 2) * 255), ((out & 1) * 255));
  }

  event void RadioControl.stopDone(error_t error) {

  }
 
}

