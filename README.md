# This is my Home Assistant configuration

## Setup
### Hardware
- Processor: i5
- RAM: 6GB
- Storage: 120 GB SSD
- Gigabit

### Software
- Home Assistant
  - Installed in a venv
- Pi-Hole
- Zoneminder

## Devices
### Lightify
- 4 A19 soft white on/off dim
- 3 A19 RGBW
- 1 RGBW recessed fixture
- 4 RGBW flex strips with a few extensions and extenders
- 5 RGB Gardenspots

### Philips Hue
- 2nd gen hub
- 5 A19 soft white on/off dim
- 4 GE links PAR38 on/off dim

### Z-wave 
- Controller: Aeotec 5th gen smart stick
- 4 GE dimmers
- 2 GE switches
- 1 GE outdoor
- 2 Monoprice outlets
- 1 Leviton outlet
- 1 Monoprice shock sensor
- 1 Monoprice garage door sensor
- 1 Schlage BE469 lock
- 2 Aeon smart switch energy meters
- 1 Aeon Siren
- 3 First Alert Combo Detectors (Smoke and CO2)

### ZHA/ZigBee 
- Controller: Go Control HUSBZB-1
- 12 Iris Contact Sensors
- 3 Cree lights
- 3 Iris smart plugs

### SmartThings (devices waiting to be ported over)
- Dishwasher power
- Mailbox sensor
- Garage Door backyard sensor
- House fan (need to figure out how to get house fan from thermostat to work)

### Xiaomi gateway
- 1 Leak sensor
- 1 contact sensor
### Other Devices
- Rachio 8 zone (1st gen)
- Honeywell Wifi Thermostat
- Bloomsky weather station
- Neato Botvac D7
- 3 Google Homes
- 3 Google Home Minis
- 2 Harmony Hubs
- 2 IR Fans
- 3 IR Curtains
- 1 IR Fireplace

### Cameras
- 2 Amcrest 1080p PTZ
- 1 Sercomm RC8021
- 1 Honeywell Lyric C2
- 1 Amcrest 720p Outdoor
- 1 Ring video doorbell (1st gen)
- 1 Ring floodlight camera

## Automations

### Alarm
- Arm the alarm when the door is locked from the outside
- Arm the alarm when nobody is home and the alarm is not on
- Disarm the alarm upon successful unlock
- Disarm the alarm when one of us get home
- Notify alarm activated
- Notify alarm deactivated
- Notify alarm on but a window is open
- Send a picture from the proper camera when the alarm is tripped
- Notify which user unlocked the door
- Run goodbye scene when the alarm is on
- Turn on the lights when the alarm turns off
- Turn on lights when door unlocked and alarm off
- Notify the keypad locked for too many attempts

### Harmony
- Close curtains facing street 30 minutes before sunset
- Turn on fireplace and TV lights if watching TV 30 minutes before the sunsets
- Turn on zone 2 when outside speakers turn on
- Turn off fireplace, TV lights and den fan when harmony is turned off
- Set proper curtain boolean values on home assistant restart
- Set proper boolean values based on harmony activity

### TTS
- Front door open/close
- Front door lock jammed
- Close den sliding door if window is not open

### Laundry Notifications
- Washer, dryer and dishwasher notifications

### Office Automations
- Turn on all office lights when the main switch is on
- Turn off all office lights when main switch is off
- Turn off office light if one comes on randomly when the main is off

### Dog Lights
- Turn on corner and front door lamp when we leave the house and the sunsets
- Turn off corner and front door lamp when alarm is deactivated or the sun rises

### Morning Automations
- Turn on lights at 730am if vacation mode is off, alarm is deactivated during the week
  - Bedroom lights, office lights and kitchen lights turn on
  - Bedroom curtains open
  - Once Tosh leaves all the lights turn off including the bedroom fan
- Remind boogie to take her meds
- Open bay window curtains, turn off house fan when the sun rises and alarm is off
- Set hallway light to daylight white if it turns on and the sun is above the horizon
- Open bedroom curtains at 10:30am on weekends if the alarm is off
- Heat up house in the morning on workdays if house is below 65 at 730am

### Lock Automations
- Start a 3 minute timer if the door is unlocked and closed
- Cancel the timer if the door is locked or open
- Lock the front door once the timer finishes and the door is still closed

### Mailbox Notifications
- Turn on mailbox boolean at sunrise
- Turn off mailbox boolean once it has been opened
- Notify about mail once opened
- Set mailbox boolean on restart

### Basic Light Automations
- Turn on/off Bedroom/Office closet light when the door is open/closed
- Turn on/off Garage lights when the backyard door is open/closed
- Turn on/off Garage lights when the frontyard is open/closed
- Turn off Bedroom/Office closet or Garage lights when left on for 15 minutes

### Windows Open
- Notify if a window is open and it is raining outside
  - Rain is based off bloomsky being and rachio being off
- Notify thermostat is on and a window is open

### Night Time Automations
- Turn on colorful lights at sunset when we get home
- Turn on colorful lights if alarm is disarmed when the sun is below the horizon
- Turn off the fans if the house gets too cold while we are sleeping

### Smoke Detector Notifications
- Den, Bedroom, Office smoke detection
- Den, Bedroom, Office CO2 detection

### Thermostat Automations
- Cool down house if thermostat is off and above 80
- Set thermostat cooling if left on and we are away
- Set thermostat heating if left on and we are away

### Movie Mode
- Movie mode turned on turns on the TV lights, turns off all other lights but the Den, turns on fireplace if it is not already on
- Close curtains if movie mode is on and the sun is above the horizon
- When Kodi is playing turn off the den lights
- When Kodi is paused for 30 seconds or idle for 1 minute turn on den and kitchen lights
- Open curtains if they were closed
