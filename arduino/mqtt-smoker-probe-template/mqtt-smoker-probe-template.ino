// Many thanks to Aderusha for the following project where 99% of this code comes from: https://github.com/aderusha/MQTTCarPresence
// In fact you need to follow the steps at that URL to get started here so do that first (including how to upload the code).  Make sure you install the MAX6675 library as well in the Adruino IDE.
// 
// Parts needed:
// ESP8266 NodeMCUv2, MAX6675 Chip, K-type thermocouple, 5 female to female dupont cables, powerbank

// MAX6675 pins     ESP8266 pins
// GND              GND
// VCC              3.3V
// SCK              GPIO12
// CS               GPIO13
// SO               GPIO15


////////////////////////////////////////////////////////////////////////////////////////////////////
// Modify these values for your environment
const char* wifiSSID = "";  // Your WiFi network name
const char* wifiPassword = "";  // Your WiFi network password
const char* otaPassword = "";  // OTA update password
const char* mqttServer = "";  // Your MQTT server IP address
const char* mqttUser = ""; // mqtt username, set to "" for no user
const char* mqttPassword = ""; // mqtt password, set to "" for no password
const String mqttNode = "BBQ"; // Your unique hostname for this device
const String mqttDiscoveryPrefix = "homeassistant"; // Home Assistant MQTT Discovery, see https://home-assistant.io/docs/mqtt/discovery/
////////////////////////////////////////////////////////////////////////////////////////////////////

// Home Assistant MQTT Discovery, see https://home-assistant.io/docs/mqtt/discovery/
// We'll create one binary_sensor device to track MQTT connectivity
const String mqttDiscoBinaryStateTopic = mqttDiscoveryPrefix + "/binary_sensor/" + mqttNode + "/state";
const String mqttDiscoBinaryConfigTopic = mqttDiscoveryPrefix + "/binary_sensor/" + mqttNode + "/config";
// And a sensor for WiFi signal strength
const String mqttDiscoTempStateTopic = mqttDiscoveryPrefix + "/sensor/" + mqttNode + "-temperature/state";
const String mqttDiscoTempConfigTopic = mqttDiscoveryPrefix + "/sensor/" + mqttNode + "-temperature/config";
// And a sensor for device uptime
//const String mqttDiscoVoltStateTopic = mqttDiscoveryPrefix + "/sensor/" + mqttNode + "-voltage/state";
//const String mqttDiscoVoltConfigTopic = mqttDiscoveryPrefix + "/sensor/" + mqttNode + "-voltage/config";

// The strings below will spill over the PubSubClient_MAX_PACKET_SIZE 128
// You'll need to manually set MQTT_MAX_PACKET_SIZE in PubSubClient.h to 512
const String mqttDiscoBinaryConfigPayload = "{\"name\": \"" + mqttNode + "\", \"device_class\": \"connectivity\", \"state_topic\": \"" + mqttDiscoBinaryStateTopic + "\"}";
const String mqttDiscoTempConfigPayload = "{\"name\": \"" + mqttNode + "-temperature\", \"state_topic\": \"" + mqttDiscoTempStateTopic + "\", \"unit_of_measurement\": \"F\", \"value_template\": \"{{ value }}\"}";
//const String mqttDiscoVoltConfigPayload = "{\"name\": \"" + mqttNode + "-voltage\", \"state_topic\": \"" + mqttDiscoVoltStateTopic + "\", \"unit_of_measurement\": \"v\", \"value_template\": \"{{ value }}\"}";

// Set the signal strength and uptime reporting interval in milliseconds
const unsigned long reportInterval = 5000;
unsigned long reportTimer = millis();

// Set LED "twinkle" time for maximum daylight visibility
const unsigned long twinkleInterval = 50;
unsigned long twinkleTimer = millis();

#include <ESP8266WiFi.h>
#include <ESP8266mDNS.h>
#include <WiFiUdp.h>
#include <ArduinoOTA.h>
#include <PubSubClient.h>
#include "max6675.h"

WiFiClient wifiClient;
PubSubClient mqttClient(wifiClient);

/*************************************************/
/* Settings for MAX6675 Measurements             */
/*************************************************/
MAX6675 thermocouple(D6, D7, D8);
String temperature;  // Values read from sensor

/*************************************************/
/* Settings for VCC Measurements                 */
/*************************************************/
//ADC_MODE(ADC_VCC);
//float espVoltage;


////////////////////////////////////////////////////////////////////////////////////////////////////
// System setup
void setup() {
  pinMode(LED_BUILTIN, OUTPUT);
  digitalWrite(LED_BUILTIN, HIGH);
  Serial.begin(115200);

  Serial.println("\nHardware initialized, starting program load");

  // Start up networking
  setupWifi();

  // Create server and assign callbacks for MQTT
  mqttClient.setServer(mqttServer, 1883);
  mqttClient.setCallback(mqtt_callback);

  // Start up OTA
  if (otaPassword[0]) {
    setupOTA();
  }

  Serial.println("Initialization complete\n");
}

////////////////////////////////////////////////////////////////////////////////////////////////////
// Main execution loop
void loop() {
  // check WiFi connection
  if (WiFi.status() != WL_CONNECTED) {
    setupWifi();
  }

  // check MQTT connection
  if (!mqttClient.connected()) {
    mqttConnect();
  }

  // MQTT client loop
  if (mqttClient.connected()) {
    mqttClient.loop();
  }

  // LED twinkle
  if (mqttClient.connected() && ((millis() - twinkleTimer) >= twinkleInterval)) {
    digitalWrite(LED_BUILTIN, !digitalRead(LED_BUILTIN));
    twinkleTimer = millis();
  }

  // Report signal strength and uptime
  if (mqttClient.connected() && ((millis() - reportTimer) >= reportInterval)) {
    //String signalStrength = String(WiFi.RSSI());
    //String uptimeTimer = String(millis());

     delay(6000);
      temperature = String(thermocouple.readFahrenheit());
      yield();
      // Determine the VCC Voltage
      //espVoltage = ESP.getVcc();
      //yield();
    mqttClient.publish(mqttDiscoTempStateTopic.c_str(), temperature.c_str());
    //mqttClient.publish(mqttDiscoVoltStateTopic, espVoltage);
    reportTimer = millis();
  }

  // OTA loop
  if (otaPassword[0]) {
    ArduinoOTA.handle();
  }
}

////////////////////////////////////////////////////////////////////////////////////////////////////
// Functions

////////////////////////////////////////////////////////////////////////////////////////////////////
// Handle incoming commands from MQTT
void mqtt_callback(char* topic, byte* payload, unsigned int payloadLength) {
}

////////////////////////////////////////////////////////////////////////////////////////////////////
// Connect to WiFi
void setupWifi() {
  Serial.print("Connecting to WiFi network: " + String(wifiSSID));
  WiFi.hostname(mqttNode.c_str());
  WiFi.mode(WIFI_STA);
  WiFi.begin(wifiSSID, wifiPassword);

  while (WiFi.status() != WL_CONNECTED) {
    // Wait 500msec seconds before retrying
    delay(500);
    Serial.print(".");
  }
  Serial.println("\nWiFi connected successfully and assigned IP: " + WiFi.localIP().toString());
}

////////////////////////////////////////////////////////////////////////////////////////////////////
// MQTT connection and subscriptions
void mqttConnect() {
  digitalWrite(LED_BUILTIN, HIGH);
  Serial.println("Attempting MQTT connection to broker: " + String(mqttServer));
  // Attempt to connect to broker, setting last will and testament
  if (mqttClient.connect(mqttNode.c_str(), mqttUser, mqttPassword, mqttDiscoBinaryStateTopic.c_str(), 1, 1, "OFF")) {
    // when connected, record signal strength and reset reporting timer
    //String signalStrength = String(WiFi.RSSI());
    reportTimer = millis();
    //String uptimeTimer = String(millis());

     //delay(6000);
      temperature = String(thermocouple.readFahrenheit());
      yield();
      // Determine the VCC Voltage
      //espVoltage = ESP.getVcc();
     // yield();
    
    // publish MQTT discovery topics and device state
    Serial.println("MQTT discovery connectivity config: [" + mqttDiscoBinaryConfigTopic + "] : [" + mqttDiscoBinaryConfigPayload + "]");
    Serial.println("MQTT discovery connectivity state: [" + mqttDiscoBinaryStateTopic + "] : [ON]");
    Serial.println("MQTT discovery temperature config: [" + mqttDiscoTempConfigTopic + "] : [" + mqttDiscoTempConfigPayload + "]");
    Serial.println("MQTT discovery temperature state: [" + mqttDiscoTempStateTopic + "] : " + temperature);
    //Serial.println("MQTT discovery voltage config: [" + mqttDiscoVoltConfigTopic + "] : [" + mqttDiscoVoltConfigPayload + "]");
    //Serial.println("MQTT discovery voltage state: [" + mqttDiscoVoltStateTopic + "] : " + espVoltage);
    mqttClient.publish(mqttDiscoBinaryConfigTopic.c_str(), mqttDiscoBinaryConfigPayload.c_str(), true);
    mqttClient.publish(mqttDiscoBinaryStateTopic.c_str(), "ON");
    mqttClient.publish(mqttDiscoTempConfigTopic.c_str(), mqttDiscoTempConfigPayload.c_str(), true);
    mqttClient.publish(mqttDiscoTempStateTopic.c_str(), temperature.c_str());
   // mqttClient.publish(mqttDiscoVoltConfigTopic.c_str(), mqttDiscoVoltConfigPayload.c_str(), true);
   // mqttClient.publish(mqttDiscoVoltStateTopic.c_str(), espVoltage);
    Serial.println("MQTT connected");
    digitalWrite(LED_BUILTIN, LOW);
  }
  else {
    Serial.println("MQTT connection failed, rc=" + String(mqttClient.state()));
  }
}

////////////////////////////////////////////////////////////////////////////////////////////////////
// (mostly) boilerplate OTA setup from library examples
void setupOTA() {
  // Start up OTA
  // ArduinoOTA.setPort(8266); // Port defaults to 8266
  ArduinoOTA.setHostname(mqttNode.c_str());
  ArduinoOTA.setPassword(otaPassword);

  ArduinoOTA.onStart([]() {
    Serial.println("ESP OTA:  update start");
  });
  ArduinoOTA.onEnd([]() {
    Serial.println("ESP OTA:  update complete");
  });
  ArduinoOTA.onProgress([](unsigned int progress, unsigned int total) {
    //Serial.printf("Progress: %u%%\r", (progress / (total / 100)));
  });
  ArduinoOTA.onError([](ota_error_t error) {
    Serial.println("ESP OTA:  ERROR code " + String(error));
    if (error == OTA_AUTH_ERROR) Serial.println("ESP OTA:  ERROR - Auth Failed");
    else if (error == OTA_BEGIN_ERROR) Serial.println("ESP OTA:  ERROR - Begin Failed");
    else if (error == OTA_CONNECT_ERROR) Serial.println("ESP OTA:  ERROR - Connect Failed");
    else if (error == OTA_RECEIVE_ERROR) Serial.println("ESP OTA:  ERROR - Receive Failed");
    else if (error == OTA_END_ERROR) Serial.println("ESP OTA:  ERROR - End Failed");
  });
  ArduinoOTA.begin();
  Serial.println("ESP OTA:  Over the Air firmware update ready");
}


// MIT License

// Copyright (c) 2017 aderusha

// Permission is hereby granted, free of charge, to any person obtaining a copy
// of this software and associated documentation files (the "Software"), to deal
// in the Software without restriction, including without limitation the rights
// to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
// copies of the Software, and to permit persons to whom the Software is
// furnished to do so, subject to the following conditions:

// The above copyright notice and this permission notice shall be included in all
// copies or substantial portions of the Software.

// THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
// IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
// FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
// AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
// LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
// OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
// SOFTWARE.