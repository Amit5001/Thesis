#include <Wire.h>
#include <Lidar_VL53L1X.h>



// Drone altitude measurement with XSHUT on pin 26
Lidar_VL53L1X lidar(true, VL53L1X::Long, 50000, 50, 5000, 26, Wire2);

void setup() {
    Serial.begin(115200);
    
    if (lidar.init_Lidar()) {
        Serial.println("Lidar ready for altitude measurement");
    } else {
        Serial.println("Lidar initialization failed!");
    }
}

void loop() {
    uint16_t distance = lidar.readDistance();
    if (distance > 0) {
        Serial.print("Altitude: ");
        Serial.print(distance);
        Serial.println(" mm");
    }
    delay(50);
}