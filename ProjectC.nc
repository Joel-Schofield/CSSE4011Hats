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

#define CMD_LED_TRACK 1
#define CMD_AUDIO_TRACK 2
#define CMD_GET_ADC 3

#define NUM_LEDS 5

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

struct {
	uint32_t eventId; //ID of the event. Used as a unique identifier.
	uint32_t commandId; //ID of the command
	uint64_t startTime; //time at which the event will start (global synced time)
	uint64_t dataLength; //data length in bytes
	void* data;
} typedef pktHeader;

struct {
	uint8_t ledColours[5][100];
	uint64_t ledTimes[100];
	uint8_t ledEventLen;
	uint8_t ledEventCnt;
} typedef ledTrack;

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
		
    	// generic components.
		interface GeneralIO as Button0;

		// sensors
		//ADC
		interface Timer<TMilli> as AdcTimer;
	    interface Read<uint16_t> as AccelX;
	    interface Read<uint16_t> as AccelY;
	    interface Read<uint16_t> as AccelZ;

		// timers
		interface Timer<TMilli> as StatusTimer;

		//leds
		interface Timer<TMilli> as LedTrackTimer;
		interface Leds;
		interface RgbLed;

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

	ledTrack currLedTrack;

	uint16_t temp = 0;

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

		// if reporting to destination is enabled, periodicaly send to the station
		send_dest.sin6_port = htons(4321);
		inet_pton6(REPORT_DEST, &send_dest.sin6_addr);
		call StatusTimer.startOneShot(5000);

		// bind to ports for each udp service
		call Echo.bind(7);
		call LedServer.bind(1234);
		call Status.bind(7001);

		//start reading from the ADC.
		call AdcTimer.startOneShot(SAMPLING_PERIOD);
		printf("Booted: %i\n", TOS_NODE_ID);
		printfflush();
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
		
		pktHeader header;

		// if the size is correct for the header radio struct
		if (len >= sizeof(header)) {

			// copy the void radio packet to the header stuct
			memcpy(&header,payload,sizeof(header));

			// if the headers command is LED_TRACK
			if (header.commandId == CMD_LED_TRACK) {

				// initilise some varables
				int cnt = 0;
				int ev = 0;
				int i = 0;

				// while i is less then the headers datalength
				while (i < header.dataLength) {

					// if count is equal to NUM_LEDS
					if (cnt == NUM_LEDS) {
						// set the current led track
						currLedTrack.ledTimes[ev] = *((uint64_t*)(payload + sizeof(header) + i));
						cnt = 0;
						ev++;
						i += 4;
					}
					//  else 
					else {
						// increment count and i and shiz
						currLedTrack.ledColours[cnt][ev] = *((uint8_t*)(payload + sizeof(header) + i));
						i++;
						cnt++;
					}
				}

				
				currLedTrack.ledEventLen = ev;
				currLedTrack.ledEventCnt = 0; //ready to play the newest led track!

				//TODO: replace oneshot time with starttime parsed in command. (needs globalTime implemented).
				call LedTrackTimer.startOneShot(0); 
			}

		}

		/*
		// check it is the correct length
		if(len == sizeof(msg))
		{
			memcpy(&msg,payload,sizeof(msg));

			// change the led colour
			printf("game ID: %u sound ID: %u R: %u G: %u B: %u\n\r",
				msg.gameId,msg.soundId,msg.red,msg.green,msg.blue);
			call RgbLed.setColorRgb(msg.red, msg.green, msg.blue);
			printfflush();
		}
		*/
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

	event void LedTrackTimer.fired() 
	  {

	    printf("ledTrackFired!\n\r");
		printfflush();

		//TODO: code for updating the led colours.

		currLedTrack.ledEventCnt++;

		if (currLedTrack.ledEventCnt < currLedTrack.ledEventLen) {

			//TODO: code is likely to have clock skew. better solution should be implemented once globaltime is implemented.
			call LedTrackTimer.startOneShot(currLedTrack.ledTimes[currLedTrack.ledEventCnt] - 
				currLedTrack.ledTimes[currLedTrack.ledEventCnt - 1]);
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
				printf("sending accelerometer\n");
				printfflush();
/*
				// make up some data
				for(temp = 0; temp < 100; temp++) {
					datax[temp] = call Random.rand16();
					datay[temp] = call Random.rand16();
					dataz[temp] = call Random.rand16();

				}
*/
				msg_send.id = TOS_NODE_ID;
				memcpy(&msg_send.dataxvar,datax,sizeof(datax));
				memcpy(&msg_send.datayvar,datay,sizeof(datay));
				memcpy(&msg_send.datazvar,dataz,sizeof(dataz));
				call Status.sendto(&send_dest, &msg_send, sizeof(msg_send));
			}
		}
	}
}
