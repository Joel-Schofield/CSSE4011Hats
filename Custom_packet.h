#ifndef _CUSTOMPACKET_H
#define _CUSTOMPACKET_H

#include <BlipStatistics.h>

typedef nx_struct udp_report {
	nx_uint16_t seqno;
	nx_uint16_t sender;
	nx_uint16_t accelerometer[100];
	ip_statistics_t    ip;
	udp_statistics_t   udp;
} ;

struct udp_receive {
	nx_uint16_t led;
	nx_uint16_t sound;
	nx_uint16_t stat;
} ;

struct radio_msg_send {

	// TOS_ID
	uint8_t id;

	// acceldata
	uint8_t data[100];
} ;

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

#endif