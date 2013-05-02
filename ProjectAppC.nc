#include <lib6lowpan/6lowpan.h>

configuration ProjectAppC
{
} 
implementation {
    // basic components
    components MainC;
    components ProjectC;

    ProjectC.Boot -> MainC;

    // timers 
    components new TimerMilliC() as t0;
    // components new TimerMilliC() as t1;
    components IPStackC;

    components ZigduinoDigitalPortsC;
    ProjectC.Button0 -> ZigduinoDigitalPortsC.Digital1;

    // rgb led driver
    components LedsC, new RgbLedC(6, 7);
    ProjectC.Leds -> LedsC;
    ProjectC.RgbLed -> RgbLedC;

    // sensors

    // networking udpsockets for different functions in program
    ProjectC.RadioControl ->  IPStackC;
    components new UdpSocketC() as Echo,
    new UdpSocketC() as Status,
    new UdpSocketC() as ledserv;

    // wire them up to the program
    ProjectC.Echo -> Echo;
    ProjectC.Status -> Status;
    ProjectC.LedServer -> ledserv;

    // wire up the timers
    ProjectC.StatusTimer -> t0;

    // dont really know what this is, but its important
    components UdpC, IPDispatchC;
    ProjectC.IPStats -> IPDispatchC;
    ProjectC.UDPStats -> UdpC;

    #ifdef RPL_ROUTING
    components RPLRoutingC;
    #endif

    // random number generator
    components RandomC;
    ProjectC.Random -> RandomC;

    // UDP shell on port 2000
    components UDPShellC;

    // time sync stuff
    components TimeSyncC;
    MainC.SoftwareInit -> TimeSyncC;
    ProjectC.TimeSyncControl -> TimeSyncC;
    ProjectC.GlobalTime -> TimeSyncC;

    // prints the routing table
    #if defined(PLATFORM_IRIS)
    #warning *** RouterCmd disabled for IRIS ***
    #else
    components RouteCmdC;
    #endif

    #ifndef  IN6_PREFIX
    components DhcpCmdC;
    #endif
}
