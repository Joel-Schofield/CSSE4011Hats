// this is csse4011 stuff
#include <lib6lowpan/6lowpan.h>


configuration ProjectAppC 
{ 
} 
implementation { 

// basic components
  components MainC, LedsC;
  components ProjectC;

  ProjectC.Boot -> MainC;
  ProjectC.Leds -> LedsC;

  // timers 
  components new TimerMilliC() as t0;
  // components new TimerMilliC() as t1;
  components IPStackC;

  components ZigduinoDigitalPortsC;
  ProjectC.Button0 -> ZigduinoDigitalPortsC.Digital1;

  // sensors
  components new LightSensorC() as Sensor;
  ProjectC.sensor1 -> Sensor;

  // networking udpsockets for different functions in program
  ProjectC.RadioControl ->  IPStackC;
  components new UdpSocketC() as Echo,
  new UdpSocketC() as Status,
  new UdpSocketC() as ledserv;

  // wire them up to the program
  ProjectC.Echo -> Echo;

  // wire up the timers
  ProjectC.StatusTimer -> t0;
  // ProjectC.Timer0 -> t1;

  // dont really know what this is, but its important
  components UdpC, IPDispatchC;
  ProjectC.IPStats -> IPDispatchC;
  ProjectC.UDPStats -> UdpC;

  #ifdef RPL_ROUTING
  components RPLRoutingC;
  #endif

  // UDP shell on port 2000
  components UDPShellC;

  #ifndef  IN6_PREFIX
  components DhcpCmdC;
  #endif

  #ifdef PRINTFUART_ENABLED
  /* This component wires printf directly to the serial port, and does
  * not use any framing.  You can view the output simply by tailing
  * the serial device.  Unlike the old printfUART, this allows us to
  * use PlatformSerialC to provide the serial driver.
  * 
  * For instance:
  * $ stty -F /dev/ttyUSB0 115200
  * $ tail -f /dev/ttyUSB0
  */
  components SerialPrintfC;

  /* This is the alternative printf implementation which puts the
  * output in framed tinyos serial messages.  This lets you operate
  * alongside other users of the tinyos serial stack.
  */
  // components PrintfC;
  // components SerialStartC;
  #endif
}
