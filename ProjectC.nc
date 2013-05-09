#include <IPDispatch.h>
#include <lib6lowpan/lib6lowpan.h>
#include <lib6lowpan/ip.h>
#include <lib6lowpan/ip.h>
#include <BlipStatistics.h>

// #include "Custom_packets.h"
#include "UdpCountToLeds.h"
#include "blip_printf.h"
#include "printf.h"

#define REPORT_PERIOD 5L

struct radio_msg {
	// led colour
	uint8_t red;
	uint8_t green;
	uint8_t blue;

	// game id
	uint8_t gameId;

	// sound id
	uint8_t soundId;
} ;

struct radio_msg_send {

	// TOS_ID
	uint8_t id;

	// acceldata
	uint16_t dataxvar[100];
	uint16_t datayvar[100];
	uint16_t datazvar[100];
} ;

module ProjectC {
	uses {
		interface Boot;

		// radio
		interface SplitControl as RadioControl;
		interface UDP as Echo;
		interface UDP as Status;
		interface UDP as LedServer;

		// time sync
		interface StdControl as TimeSyncControl;
		interface LocalTime<TMilli>;
    	interface GlobalTime<TMilli>;
		
    	// generic components
		interface Leds;
		interface RgbLed;
		interface GeneralIO as Button0;

		// sensors
		//ADC
		interface Timer<TMilli> as AdcTimer;
	    interface Read<uint16_t> as AccelX;
	    interface Read<uint16_t> as AccelY;
	    interface Read<uint16_t> as AccelZ;

		// timers
		interface Timer<TMilli> as StatusTimer;

		// ipv6lopan statistics
		// interface BlipStatistics<ip_statistics_t> as IPStats;
		// interface BlipStatistics<udp_statistics_t> as UDPStats;

		// random number genorator for transmission
		interface Random;
	}

} implementation {

	bool timerStarted;
	nx_struct udp_report stats;
	struct sockaddr_in6 route_dest;
	struct sockaddr_in6 send_dest;

	// timer variables
	uint32_t refLocalTime = 0;
  	uint32_t refGlobalTime = 0;

  	// ADC variables
  	uint16_t lastX = 0;
	uint16_t lastY = 0;
	uint16_t lastZ = 0;
	uint16_t SAMPLING_PERIOD = 100; //adc sample period in millisecs

	// data from the accelerometer
	uint16_t datax[100];
	uint16_t datay[100];
	uint16_t dataz[100];

	uint8_t dataxplace = 0;
	uint8_t datayplace = 0;
	uint8_t datazplace = 0;

	// custom radiopacket
	// the receive radio packet
	struct radio_msg msg;
	// the send radio packet
	struct radio_msg_send msg_send;
	uint8_t counter;
	struct sockaddr_in6 dest;

	event void Boot.booted() {
		
		// start the radio
		call RadioControl.start();
		call Button0.makeInput();
		timerStarted = FALSE;

		// call IPStats.clear();
		// call Timer0.startPeriodic(700);

		// if reporting to destination is enabled, periodicaly send to the station
		send_dest.sin6_port = htons(4321);
		inet_pton6("fec0::100", &send_dest.sin6_addr);
		call StatusTimer.startOneShot(5000);

		// bind to ports for each udp service
		call Echo.bind(7);
		call LedServer.bind(1234);
		call Status.bind(7001);

		//start reading from the ADC.
		call AdcTimer.startOneShot(SAMPLING_PERIOD);
		dbg("Boot", "booted: %i\n", TOS_NODE_ID);
	}

	event void RadioControl.startDone(error_t e) {
		// no need to implement
	}

	event void RadioControl.stopDone(error_t e) {
		// no need to implement
	}

	// when you receive on port 1234 do the following
	event void LedServer.recvfrom(struct sockaddr_in6 *src, void *payload, 
									uint16_t len, struct ip6_metadata *meta) {   
		memcpy(&msg,payload,sizeof(msg));
		// check it is the correct length
		if(len == sizeof(msg))
		{
			// change the led colour
			printf("game ID: %u sound ID: %u R: %u G: %u B: %u\n\r",
				msg.gameId,msg.soundId,msg.red,msg.green,msg.blue);
			call RgbLed.setColorRgb(msg.red, msg.green, msg.blue);
			printfflush();
		}
	}


	event void Status.recvfrom(struct sockaddr_in6 *from, void *data, 
			 						uint16_t len, struct ip6_metadata *meta) {
		// no need to implement this 
	}

	// when you receive something on port 7
	event void Echo.recvfrom(struct sockaddr_in6 *from, void *data, 
							   uint16_t len, struct ip6_metadata *meta) {
		// remove when theres time
	}

	// status update timer fired for sending on port 7001
	event void StatusTimer.fired() {	
		call Leds.led0Toggle();
		if (!timerStarted) {
			call StatusTimer.startPeriodic(5000);
			timerStarted = TRUE;
			call RgbLed.setColorRgb(0, 0, 0);
		}
	}

	event void AdcTimer.fired() 
	  {

	    call AccelX.read();
	    call AccelY.read();
	    call AccelZ.read();

	    printf("readVal: xyz: %u, %u, %u\n\r", lastX-450, lastY-450, lastZ-450);
			printfflush();

		call AdcTimer.startOneShot(SAMPLING_PERIOD);
	  }

	event void AccelX.readDone(error_t result, uint16_t val) {
		if (result == SUCCESS) {
			lastX = val;
			
			// store the data
			datax[dataxplace] = val;
			dataxplace++;

			// check for overflow
			if(dataxplace == 100) {
				dataxplace = 0;
			}
		}
	}
	event void AccelY.readDone(error_t result, uint16_t val) {
		if (result == SUCCESS) {
			lastY = val;

			// store the data
			datay[datayplace] = val;
			datayplace++;

			// check for overflow
			if(datayplace == 100) {
				datayplace = 0;
			}
		}
	}
	event void AccelZ.readDone(error_t result, uint16_t val) {
		if (result == SUCCESS) {
			lastZ = val;

			// store the data
			dataz[datazplace] = val;
			datazplace++;

			// check for overflow
			if(datazplace == 100) {
				// reset the data
				datazplace = 0;
				// send the data
				call Status.sendto(&report_dest, &msg_send, sizeof(msg_send));
			}
		}
	}
}
