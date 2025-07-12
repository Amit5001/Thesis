#ifndef LIDAR_VL53L1X_H
#define LIDAR_VL53L1X_H

#include <Arduino.h>
#include <Wire.h>
#include <VL53L1X.h>
/*
@param io_2v8: true for 2.8V I/O, false for 1.8V I/O. Must match the microcontroller's output voltage.
@param distance_mode: Distance mode to use (Short 1.3m, Medium 2.9m, Long 4m). 
@param timing_budget: Measurement timing budget in microseconds. depends on distance mode. 20-1000ms (20,000 - 1,000,000 us).
                      Short - 20000, Medium - 33000, Long - 33000.
                      Longer budget allows for more accurate measurements.
                      Longer budget produce greater maximum range, higher power consumption, slower measurement rate.
@param measurement_period: Measurement period in milliseconds. Default is 100ms.
                          This is the time between consecutive measurements.
                          If shorter than timing budget, new measurement starts after the previous one finishes.
                          If longet than timing budget, the sensor will wait for the next period to start a new measurement.
                          Lower value = faster measurements, but higher power consumption.
@param timeout: Timeout for I2C communication in milliseconds. Default is 10000ms.
                 If the sensor does not respond within this time, an error will be returned.
                 This is useful to avoid blocking the program if the sensor is not responding.
@param ROIsize: Region of Interest (ROI) size in pixels. Default is 16x16 pixels.
                 This defines the area of the sensor's field of view to be used for measurements.
                 Smaller ROI size can improve measurement speed and accuracy, but may reduce maximum range.

Parameter            | Increase Value                           | Decrease Value
---------------------|------------------------------------------|------------------------------------------
Timing Budget        | ^ Accuracy, ^ Range, ^ Power, v Speed    | v Accuracy, v Range, v Power, ^ Speed
Measurement Period   | v Data Rate, v Power                     | ^ Data Rate, ^ Power
Distance Mode        | Long->Short: v Range, ^ Ambient Immunity | Short->Long: ^ Range, v Ambient Immunity
ROI Size             | ^ Sensitivity, ^ FoV, ^ Range            | v Sensitivity, v FoV, v Range, ^ Precision

For Drone Altitude:
    VL53L1XSensor lidar(true, VL53L1X::Long, 50000, 50, 5000);
    Timing budget: 50ms (50000us) for Long distance mode
    Measurement period: 50ms (50ms) for continuous measurements
    Timeout: 5000ms (5s) for I2C communication
    ROI size: 16x16 pixels (default)


For Indoor:
    VL53L1XSensor lidar(true, VL53L1X::Short, 50000, 50, 5000);
    Timing budget: 50ms (50000us) for Short distance mode
    Measurement period: 50ms (50ms) for continuous measurements
    Timeout: 5000ms (5s) for I2C communication
    ROI size: 16x16 pixels (default)

For High-speed Detection:
    VL53L1XSensor lidar(true, VL53L1X::Medium, 33000, 20, 5000);
    Timing budget: 33ms (33000us) for Medium distance mode
    Measurement period: 20ms (20ms) for continuous measurements
    Timeout: 5000ms (5s) for I2C communication
    ROI size: 16x16 pixels (default)

*/
// Need To find to which I2C bus the sensor will be connected

class Lidar_VL53L1X {
public:
    Lidar_VL53L1X(bool io_2v8 = true,
                    VL53L1X::DistanceMode distance_mode = VL53L1X::Long,
                    uint32_t timing_budget = 100000,
                    uint32_t measurement_period = 100,
                    uint16_t timeout = 10000,
                    int8_t xshut_pin = 26,
                    TwoWire &i2c_bus = Wire2)
        : io_2v8(io_2v8),
          distance_mode(distance_mode),
          timing_budget(timing_budget),
          measurement_period(measurement_period),
          timeout(timeout),
          xshut_pin(xshut_pin),
          i2c_bus(i2c_bus)
    {
    }
    
    bool init_Lidar();
    float readDistance();
    bool dataReady();
    VL53L1X::RangeStatus getRangeStatus();
    float getPeakSignalRate();
    float getAmbientRate();
    void stopContinuous();
    void startContinuous();
    uint16_t readSingle(bool blocking = true);
    void resetSensor();

private:
    VL53L1X sensor;
    bool io_2v8;
    VL53L1X::DistanceMode distance_mode;
    uint32_t timing_budget;
    uint32_t measurement_period;
    uint16_t timeout;
    int8_t xshut_pin;
    TwoWire &i2c_bus;
    
    void initXSHUT();
};

#endif