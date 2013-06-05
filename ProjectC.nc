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
#define CMD_START_STREAM_ACCEL 3
#define CMD_STOP_STREAM_ACCEL 4

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

	//time of send.
	uint32_t globalTime;

	// acceldata
	uint16_t dataxvar[100];
	uint16_t datayvar[100];
	uint16_t datazvar[100];
} ;

struct {
	uint32_t eventId; //Used to uniquely identify the event.
	uint32_t commandId; //ID of the command
	uint64_t startTime; //time at which the cmd will start.
	uint64_t dataLength; //data length in bytes
} typedef pktHeader;

struct {
	uint8_t ledColours[100][5][3]; //first element is the event, 2nd is which led (1-NUM_LEDS), 3rd is each colour element (RGB).
	uint32_t ledTimes[100]; //first event time should always be 0. track times do not involve global time, and are relative.
	uint8_t ledEventLen;
	uint8_t ledEventCnt;
} typedef ledTrack;

struct {
	uint16_t audFreqs[100];
	uint32_t audTimes[100];
	uint8_t audEventLen;
	uint8_t audEventCnt;
} typedef audTrack;


uint8_t redsTest[] = {255, 0, 255, 0, 255};
uint8_t greensTest[] = {0, 255, 0, 255, 0};
uint8_t bluesTest[] = {0, 0, 0, 0, 0};

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

		//gyro
		//interface Gyro;

		//audio
		interface Timer<TMilli> as AudTrackTimer;

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
	audTrack currAudTrack;

	uint16_t temp = 0;

	int syncedAtLeastOnce = 0;

	// timer variables
	uint32_t refLocalTime = 0;
  	uint32_t refGlobalTime = 0;

  	// ADC variables
  	uint16_t lastX = 0;
	uint16_t lastY = 0;
	uint16_t lastZ = 0;
	uint16_t SAMPLING_PERIOD = 50; //adc sample period in millisecs

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
		call StatusTimer.startOneShot(0);

		// bind to ports for each udp service
		call Echo.bind(7);
		call LedServer.bind(1234);
		call Status.bind(7001);

		//start reading from the ADC. <EDIT> no longer starts here, starts once global time is synced.
		//call AdcTimer.startOneShot(SAMPLING_PERIOD);
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

		pktHeader header; //TODO: migrate to use pointer, no advantage to copying data.
		unsigned char* ptr;

		ptr = payload;

		// if the size is correct for the header radio struct
		if (len >= sizeof(header)) {

			// copy the void radio packet to the header stuct
			memcpy(&header,payload,sizeof(header));

			// if the headers command is LED_TRACK
			if (header.commandId == CMD_LED_TRACK) {

				// initilise some variables
				int ledId = NUM_LEDS; //which led we are looking at
				int col = 0; //which colour (RGB)
				int ev = 0; //event count
				int i = 0;

				while (i < header.dataLength) {

					if (ledId == NUM_LEDS) {

						currLedTrack.ledTimes[ev] = *((uint32_t*)(payload + 24 + i));
						ledId = 0;
						i += 4;
					}
					else {
						// process the ledtrack.
						currLedTrack.ledColours[ev][ledId][col] = *((uint8_t*)(payload + 24 + i));

						col++;

						if (col == 3) { //3 as one for each primary light colour.
							col = 0;
							ledId++;
						}

						if (ledId == NUM_LEDS) //finished this event, move to next one.
							ev++;

						i++;
					}
				}


				for (i=0; i < 70; i++)
					printf("%02x:", ptr[i]);

				printf("\n\r");

				printf("event Id: %lu\n\r", header.eventId);
				printf("cmd Id: %lu\n\r", header.commandId);
				printf("ledTimes: %lu\n\r", currLedTrack.ledTimes[0]);
				printf("ledTimes: %lu\n\r", currLedTrack.ledTimes[1]);



				printf("\n\r");

				printfflush();

				
				currLedTrack.ledEventLen = ev;
				currLedTrack.ledEventCnt = 0; //ready to play the newest led track!

				//TODO: replace oneshot time with starttime parsed in command. (needs globalTime implemented).

				call GlobalTime.getGlobalTime(&refGlobalTime);

				if (header.startTime > refGlobalTime) //only delay if startime is past current global time
					call LedTrackTimer.startOneShot(header.startTime - refGlobalTime); 
				else
					call LedTrackTimer.startOneShot(0);

			}

			else if (header.commandId == CMD_AUDIO_TRACK) {

				int i = 0; //byte count
				int ev = 0; //event count

				while (i < header.dataLength) {

					currAudTrack.audTimes[ev] = *((uint32_t*)(payload + 24 + i));
					i += 4;

					currAudTrack.audFreqs[ev] = *((uint16_t*)(payload + 24 + i));
					i += 2;

					ev++;

				}

				for (i=0; i < 50; i++)
					printf("%02x:", ptr[i]);

				currAudTrack.audEventLen = ev;
				currAudTrack.audEventCnt = 0; //ready to play the newest audio track!

				//TODO: replace oneshot time with starttime parsed in command. (needs globalTime implemented).

				call GlobalTime.getGlobalTime(&refGlobalTime);

				if (header.startTime > refGlobalTime) //only delay if startime is past current global time
					call AudTrackTimer.startOneShot(header.startTime - refGlobalTime); 
				else
					call AudTrackTimer.startOneShot(0);

			}

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

		int i;

		call Leds.led0Toggle();

		if (!timerStarted) {
			call StatusTimer.startPeriodic(4000); 
			timerStarted = TRUE;

			currLedTrack.ledTimes[0] = 0;
			currLedTrack.ledTimes[1] = 1000;
			currLedTrack.ledTimes[2] = 2000;
			currLedTrack.ledTimes[3] = 3000;

			currLedTrack.ledEventLen = 4;
			currLedTrack.ledEventCnt = 0;

			for (i=0; i < 5; i++) {
				currLedTrack.ledColours[0][i][0] = 255;
				currLedTrack.ledColours[0][i][1] = 0;
				currLedTrack.ledColours[0][i][2] = 0;
			}

			for (i=0; i < 5; i++) {
				currLedTrack.ledColours[1][i][0] = 0;
				currLedTrack.ledColours[1][i][1] = 255;
				currLedTrack.ledColours[1][i][2] = 0;
			}
			for (i=0; i < 5; i++) {
				currLedTrack.ledColours[2][i][0] = 255;
				currLedTrack.ledColours[2][i][1] = 0;
				currLedTrack.ledColours[2][i][2] = 0;
			}
			for (i=0; i < 5; i++) {
				currLedTrack.ledColours[3][i][0] = 0;
				currLedTrack.ledColours[3][i][1] = 255;
				currLedTrack.ledColours[3][i][2] = 0;
			}

			//call RgbLed.setMultRgb(redsTest, greensTest, bluesTest, NUM_LEDS);

			//call LedTrackTimer.startOneShot(0);

			//Example:
			//1) Initialize pwm:
			
			PRR1 &=    ~(1 << 3);
            OCR3A = 0X1A45;
            TCCR3B |= (1<<3)|(1<<0);  
			//2) Active pwm:
			TCCR3A |=    (1 << 6);

			//3) Deactive pwm:
			TCCR3A &=    ~(1 << 6);


			//dummy audtrack.
			currAudTrack.audFreqs[0] = 0X1A45;
			currAudTrack.audFreqs[1] = 0X2045;
			currAudTrack.audFreqs[2] = 0X2A45;
			currAudTrack.audFreqs[3] = 0X2045;
			currAudTrack.audFreqs[3] = 0X1A45;
			currAudTrack.audFreqs[3] = 0X1A45;
			currAudTrack.audFreqs[3] = 0X1A45;

			currAudTrack.audTimes[0] = 0;
			currAudTrack.audTimes[1] = 1000;
			currAudTrack.audTimes[2] = 2000;
			currAudTrack.audTimes[3] = 3000;
			currAudTrack.audTimes[4] = 4000;


			currAudTrack.audEventLen = 5;
			currAudTrack.audEventCnt = 0;

			//call AudTrackTimer.startOneShot(0);
			
		}

		if (call GlobalTime.getGlobalTime(&refGlobalTime) == SUCCESS) {

			printf("time is synced %lu!\n\r", refGlobalTime);

			if (!syncedAtLeastOnce) }
				call AdcTimer.startOneShot(5000 - (refGlobalTime % 5000) + TOS_NODE_ID*50 ); //improves times on when the adc transmits.
				
				call AudTrackTimer.startOneShot(0);

				syncedAtLeastOnce = 1;
			}

		}
		else {
			printf("time is not synced :(\n\r");
			currLedTrack.ledEventCnt = 0; //reset and play again
			call LedTrackTimer.startOneShot(0); //play the default "not synced" track.

			if (!syncedAtLeastOnce) { //send a data stream packet containing null info to let the PC know the node is active

				msg_send.id = TOS_NODE_ID;

				msg_send.globalTime = 0;

				memset(&msg_send.dataxvar,0,sizeof(datax));
				memset(&msg_send.datayvar,0,sizeof(datay));
				memset(&msg_send.datazvar,0,sizeof(dataz));

				call Status.sendto(&send_dest, &msg_send, sizeof(msg_send));
			}
		}
	}

	event void LedTrackTimer.fired() 
	  {

	  	uint8_t reds[NUM_LEDS];
		uint8_t greens[NUM_LEDS];
		uint8_t blues[NUM_LEDS];

		int i;

	    printf("ledTrackFired!\n\r");
		printfflush();

		for (i=0; i < NUM_LEDS; i++) {
			reds[i] = currLedTrack.ledColours[currLedTrack.ledEventCnt][i][0];
			greens[i] = currLedTrack.ledColours[currLedTrack.ledEventCnt][i][1];
			blues[i] = currLedTrack.ledColours[currLedTrack.ledEventCnt][i][2];
		}
		
		//update the leds.
		call RgbLed.setMultRgb(reds, greens, blues, NUM_LEDS);
		
		currLedTrack.ledEventCnt++;

		if (currLedTrack.ledEventCnt < currLedTrack.ledEventLen) {

			//TODO: code is likely to have clock skew. better solution should be implemented once globaltime is implemented.
			call LedTrackTimer.startOneShot(currLedTrack.ledTimes[currLedTrack.ledEventCnt] - 
				currLedTrack.ledTimes[currLedTrack.ledEventCnt - 1]);
		}
	}


	event void AudTrackTimer.fired() {

		//TODO: code to make beeps.

	
            OCR3A = currAudTrack.audFreqs[currAudTrack.audEventCnt];
			
			
			if (currAudTrack.audFreqs[currAudTrack.audEventCnt] != 0)
				TCCR3A |=    (1 << 6); //2) Active pwm:
			else
				TCCR3A &=    ~(1 << 6); //deactivate pwm


		currAudTrack.audEventCnt++;

		if (currAudTrack.audEventCnt < currAudTrack.audEventLen) {

			//TODO: code is likely to have clock skew. better solution should be implemented once globaltime is implemented.
			call AudTrackTimer.startOneShot(currAudTrack.audTimes[currAudTrack.audEventCnt] - 
				currAudTrack.audTimes[currAudTrack.audEventCnt - 1]);
		}
	}

	event void AdcTimer.fired() 
	  {
	    call AccelX.read();
	    call AccelY.read();
	    call AccelZ.read();

	    //printf("readVal: xyz: %u, %u, %u\n\r", lastX-450, lastY-450, lastZ-450);
		//printfflush();

		call AdcTimer.startOneShot(SAMPLING_PERIOD);
	}

	event void AccelX.readDone(error_t result, uint16_t val) {
		if (result == SUCCESS) {
			lastX = val;
			
			// store the data
			datax[dataxplace] = (val -450);
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
			datay[datayplace] = (val - 450);
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
			dataz[datazplace] = (val - 450);
			datazplace++;

			// check for overflow
			if(datazplace == 100) {
				// reset the data
				datazplace = 0;
				// send the data
				printf("sending accelerometer\n\r");
				printfflush();
				
				// pack the data
				msg_send.id = TOS_NODE_ID;

				if (call GlobalTime.getGlobalTime(&refGlobalTime) == SUCCESS)
					msg_send.globalTime = refGlobalTime;
				else
					msg_send.globalTime = 0;

				memcpy(&msg_send.dataxvar,datax,sizeof(datax));
				memcpy(&msg_send.datayvar,datay,sizeof(datay));
				memcpy(&msg_send.datazvar,dataz,sizeof(dataz));
				call Status.sendto(&send_dest, &msg_send, sizeof(msg_send));
			}
		}
	}
}
