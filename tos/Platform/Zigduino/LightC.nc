

generic configuration LightC(uint8_t channel) {
  provides interface Read<uint16_t>;
}
implementation {
  components new AdcReadClientC(), new ZigduinoAdcConfigC(channel, 1);

  Read = AdcReadClientC;
  AdcReadClientC.Atm128AdcConfig -> ZigduinoAdcConfigC;
}
