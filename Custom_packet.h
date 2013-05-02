#ifndef _CUSTOMPACKET_H
#define _CUSTOMPACKET_H

#include <BlipStatistics.h>

struct udp_report {
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

#endif