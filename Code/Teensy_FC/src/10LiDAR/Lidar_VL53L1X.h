#ifndef LIDAR_VL53L1X_H
#define LIDAR_VL53L1X_H

#include <Arduino.h>
#include <Wire.h>
#include <VL53L1X.h>

class Lidar_VL53L1X {
public:
    Lidar_VL53L1X(ODR, uint8_t address = 0x29)
        : lidar(address) {
        lidar.setTimeout(500);
        lidar.setMeasurementTimingBudget(ODR);
    }
    void begin();
    float readDistance();

private:
    VL53L1X lidar;
};

#endif