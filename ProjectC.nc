module ProjectC {
  uses {
    interface Boot;
    interface SplitControl as RadioControl;

    // udp interfaces, one to echo back, one to update to the base station and one for udpleds
    interface UDP as Echo;

    interface Leds;

    // sensors
    interface Read<uint16_t> as sensor1;

    interface Timer<TMilli> as StatusTimer;

    interface BlipStatistics<ip_statistics_t> as IPStats;
    interface BlipStatistics<udp_statistics_t> as UDPStats;
  }

} 

implementation {

  bool timerStarted;
  nx_struct udp_report stats;
  struct sockaddr_in6 route_dest;
  struct sockaddr_in6 report_dest;
  uint16_t lightSensorData = 0;

  // custom radiopacket
  radio_count_msg_t radio_payload;
  uint8_t counter;
  struct sockaddr_in6 dest;

  event void Boot.booted() {
    // start the radio
    call RadioControl.start();
    call Button0.makeInput();
    timerStarted = FALSE;

    call IPStats.clear();

    // if reporting to destination is enabled, periodicaly send to the station
    #ifdef REPORT_DEST
    report_dest.sin6_port = htons(7000);
    inet_pton6(REPORT_DEST, &report_dest.sin6_addr);
    call StatusTimer.startOneShot(5000);
    #endif

    dbg("Boot", "booted: %i\n", TOS_NODE_ID);

    // bind to ports for each udp service
    call Echo.bind(7);
  }

  event void RadioControl.startDone(error_t e) {
    // no need to implement
  }

  event void RadioControl.stopDone(error_t e) {
    // no need to implement
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

    stats.seqno++;
    stats.sender = TOS_NODE_ID;
    stats.interval = REPORT_PERIOD;

    call IPStats.get(&stats.ip);
    call UDPStats.get(&stats.udp);
    call Status.sendto(&report_dest, &stats, sizeof(stats));
  }
}

