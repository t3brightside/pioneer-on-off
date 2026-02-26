## Pioneer ON/OFF

It is designed to control a Pioneer Amplifier by emulating an Infrared (IR) signal, sent over a hardwired 3.5mm "Control In" jack.

 ### How it works

 Arduino sends the pulse and Python script is there to do if on desired conditions. I'm using Python to check if there's music playing on ALSA to switch the amp on, and off again if it's been idling for a  while.
