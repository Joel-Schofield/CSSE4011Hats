#include <IPDispatch.h>
#include <lib6lowpan/lib6lowpan.h>
#include <lib6lowpan/ip.h>
#include <lib6lowpan/ip.h>

#include "Custom_packets.h"
#include "UdpCountToLeds.h"
#include "blip_printf.h"
#include "printf.h"

#define REPORT_PERIOD 5L

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
		// add the acel here

		// timmers
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
	struct sockaddr_in6 report_dest;
	uint16_t lightSensorData = 0;
	uint8_t val = 0;

	// timer stuff
	uint32_t refLocalTime = 0;
  	uint32_t refGlobalTime = 0;

	// custom radiopacket
	// may need to init this
	nx_struct radio_payload msg;
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
		#ifdef REPORT_DEST
		report_dest.sin6_port = htons(7000);
		inet_pton6(REPORT_DEST, &report_dest.sin6_addr);
		call StatusTimer.startOneShot(5000);
		#endif

		dbg("Boot", "booted: %i\n", TOS_NODE_ID);

		// bind to ports for each udp service
		call Echo.bind(7);
		call LedServer.bind(1234);
		call Status.bind(7001);
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
		// get the payload
		nx_struct radio_msg * msg = payload;
		// check it is the correct length
		if(len == sizeof(nx_struct radio_msg))
		{
			// change the led colour
			call RgbLed.setColorRgb(msg->red, msg->green, msg->blue);
			printf("game ID: %u sound ID: %u\n\r", msg->gameId,msg->soundId);
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
		// for echoing the netcat data
		#ifdef PRINTFUART_ENABLED
		int i;
		uint8_t *cur = data;
		printf("Echo recv [%i]: ", len);
		for (i = 0; i < len; i++) {
			printf("%02x ", cur[i]);
		}
		printf("\n");
		#endif
	}

	// status update timer fired for sending on port 7001
	event void StatusTimer.fired() {	
		call Leds.led0Toggle();
		if (!timerStarted) {
			call StatusTimer.startPeriodic(5000);
			timerStarted = TRUE;
			call RgbLed.setColorRgb(0, 0, 0);
		}

		call RgbLed.setColorRgb(val++, val++, val++);

		/*?
		stats.seqno++;
		stats.sender = TOS_NODE_ID;
		stats.interval = REPORT_PERIOD;
		stats.sensor = lightSensorData;
		*/

		//call IPStats.get(&stats.ip);
		//call UDPStats.get(&stats.udp);
		//call Status.sendto(&report_dest, &stats, sizeof(stats));
	}
}
