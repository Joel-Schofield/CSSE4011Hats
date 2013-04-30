// this is csse4011 stuff


configuration ProjectAppC 
{ 
} 
implementation { 
  
  components ProjectC, MainC, new TimerMilliC() as BlinkTimerMilli;

  // basic components
  ProjectC.Boot -> MainC;
  ProjectC.BlinkTimer -> BlinkTimerMilli;
  
  // rgb led driver
  components LedsC, new RgbLedC(6, 7);
  ProjectC.Leds -> LedsC;
  ProjectC.RgbLed -> RgbLedC;
  
  // radio ip stack
  components IPStackC;
  ProjectC.RadioControl ->  IPStackC;

#ifdef RPL_ROUTING
  components RPLRoutingC;
#endif

  // UDP shell on port 2000
  components UDPShellC;
  components RouteCmdC;

  // printf on serial port
  components SerialPrintfC, SerialStartC;

  components LocalTimeMilliC;
  ProjectC.LocalTime -> LocalTimeMilliC;
  
  components TimeSyncC;
  MainC.SoftwareInit -> TimeSyncC;
  ProjectC.TimeSyncControl -> TimeSyncC;
  ProjectC.GlobalTime -> TimeSyncC;
}
