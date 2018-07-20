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
- Influxdb/Grafana
- Node-red
- HADashboard
- AppDaemon

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
- 1 Honeywell z-wave thermostat

### ZHA/ZigBee 
- Controller: Go Control HUSBZB-1
- 12 Iris Contact Sensors
- 3 Cree lights
- 3 Iris smart plugs
- 1 Iris motion sensor

### Xiaomi gateway
- 4 Leak sensor
- 4 Contact sensor
- 1 Motion sensor
- 1 Temperature sensor
- 3 Air Purifiers

### Other Devices
- Rachio 8 zone (1st gen)
- Bloomsky weather station
- Neato Botvac
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
- 1 Ring video doorbell (2nd gen)
- 1 Ring floodlight camera
- 1 Yi Dome 1080p

### DIY
- 1 ESP8266 for MQTTCarPresence project

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
- Arm the alarm when we go to bed
- Disarm when the first person wakes up

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

### Dog Lights
- Turn on corner and front door lamp when we leave the house and the sunsets
- Turn off corner and front door lamp when alarm is deactivated or the sun rises

### Morning Automations
- Turn on lights at 730am if vacation mode is off, alarm is deactivated during the week
  - Bedroom lights, office lights, living room lights, den lights and kitchen lights turn on
  - Bedroom curtains open
  - Once Tosh leaves all the lights turn off including the bedroom fan
- Remind boogie to take her meds
- Open bay window curtains, turn off house fan when the sun rises and alarm is off
- Set hallway light to daylight white if it turns on and the sun is above the horizon
- Open bedroom curtains at 10:30am on weekends if the alarm is off
- Heat up house in the morning on workdays if house is below 65 at 730am
- Turn on den lights when Danny wakes up for a call
- If den lights turn on between 4-8am set them to lowest setting
- Turn up den lights to 30% at 9am if not already

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
- Turn on bedroom lights when door opens or motion is detected, turn off lights when door is closed and no motion detected

### Windows Open
- Notify if a window is open and it is raining outside
  - Rain is based off bloomsky being and rachio being off
- Notify thermostat is on and a window is open

### Night Time Automations
- Turn on colorful lights at sunset when we get home
- Turn on colorful lights if alarm is disarmed when the sun is below the horizon
- Turn off the fans if the house gets too cold while we are sleeping
- Turn on sleep tracking on our phones when in night mode

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

### Water heater
- Notify me if rain is getting into the water heater
- Notify me if the water heater is leaking

### Battery alerts
- Check for low battery levels at 10 am and 6pm
- Clear battery alerts once fixed

### Log notifications
- Notify me if "timer out of sync" occurs

### Speed test automation
- Run a speed test if nothing is downloading or streaming at set intervals

### Numeric automations
- Notify me if SSL cert is expiring in 5 days
- Notify me if hass HDD is filing up

### Shower automations
- Turn on shower mode if humidity is above 75% for 1 minute
- Turn on KROQ radio in the bathroom when shower mode is enabled
- Turn on house fan when shower mode comes on
- Send TTS to bathroom speaker asking them to open bathroom window if not already open
- End shower mode once speaker stops or other conditions are met

### Ring automations
- Notify me on the TV when motion or doorbell is detected

### Sink leaking automations
- Notify me if any of the sinks are leaking

## Screenshots
![home1](https://user-images.githubusercontent.com/1634145/35309383-102d3826-0061-11e8-9392-eaf853efe7ea.JPG)
![home2](https://user-images.githubusercontent.com/1634145/35309377-0f99e134-0061-11e8-8567-35f34da1ace3.JPG)
![home3](https://user-images.githubusercontent.com/1634145/35309378-0fb19d60-0061-11e8-9336-efc86757ff46.JPG)
![home4](https://user-images.githubusercontent.com/1634145/35309379-0fcf4766-0061-11e8-8d96-d86205e61e24.JPG)
![home5](https://user-images.githubusercontent.com/1634145/35309380-0fe4f4e4-0061-11e8-8d8f-8f84e9e2c4a7.JPG)
![home6](https://user-images.githubusercontent.com/1634145/35309381-0ffe3e90-0061-11e8-8ee5-f96ba553957c.JPG)
![home7](https://user-images.githubusercontent.com/1634145/35309382-101375a8-0061-11e8-9053-14c6605a8edf.JPG)

## Lovelace Screenshots
![lovelace1](https://user-images.githubusercontent.com/1634145/43029010-39611fe2-8c38-11e8-9b5b-911e13c4b5c4.png)
![lovelace2](https://user-images.githubusercontent.com/1634145/43029011-398ecee2-8c38-11e8-9b1a-8aff963ca405.png)
![lovelace3 png](https://user-images.githubusercontent.com/1634145/43029012-39a71ba0-8c38-11e8-9844-48d2db1e562d.jpg)
![lovelace4](https://user-images.githubusercontent.com/1634145/43029013-39bf2402-8c38-11e8-86c9-fd254b369a96.png)
![lovelace5](https://user-images.githubusercontent.com/1634145/43029014-39d9e7a6-8c38-11e8-9261-424da0f43632.png)
![lovelace6](https://user-images.githubusercontent.com/1634145/43029015-39f0d6fa-8c38-11e8-887c-47eba75921d9.png)
![lovelace7](https://user-images.githubusercontent.com/1634145/43029016-3a08a35c-8c38-11e8-8db0-b2aa1490b6c8.png)
![lovelace8](https://user-images.githubusercontent.com/1634145/43029017-3a25437c-8c38-11e8-9de4-f83ab415794f.png)
![lovelace9](https://user-images.githubusercontent.com/1634145/43029018-3a455a22-8c38-11e8-9b93-da64730be438.png)

Special shout out to all of the various GitHub Repo's I had used in here.  Lots of people to list here but many members of the Home Assistant community contributed.
