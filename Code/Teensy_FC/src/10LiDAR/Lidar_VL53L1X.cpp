#include "Lidar_VL53L1X.h"

bool Lidar_VL53L1X::init_Lidar() {
    // Initialize I2C bus
    i2c_bus.begin();
    i2c_bus.setClock(400000);
    
    // Configure sensor to use the specified I2C bus
    sensor.setBus(&i2c_bus);
    
    // Initialize XSHUT pin if specified
    initXSHUT();
    
    // Perform sensor reset sequence if XSHUT pin is available
    if (xshut_pin >= 0) {
        resetSensor();
    }
    
    // Set timeout for sensor operations
    sensor.setTimeout(timeout);
    
    // Initialize the sensor with I/O voltage mode
    if (!sensor.init(io_2v8)) {
        Serial.println("Failed to initialize VL53L1X sensor");
        return false;
    }
    
    // Configure distance mode
    if (!sensor.setDistanceMode(distance_mode)) {
        Serial.println("Failed to set distance mode");
        return false;
    }
    
    // Set measurement timing budget
    if (!sensor.setMeasurementTimingBudget(timing_budget)) {
        Serial.println("Failed to set measurement timing budget");
        return false;
    }
    
    // Configure Region of Interest (ROI) to full 16x16 array
    sensor.setROISize(8, 8);
    sensor.setROICenter(199); // Default center SPAD
    
    // Start continuous ranging measurements
    sensor.startContinuous(measurement_period);
    
    // Serial.println("VL53L1X sensor initialized successfully");
    return true;
}

void Lidar_VL53L1X::initXSHUT() {
    if (xshut_pin >= 0) {
        pinMode(xshut_pin, OUTPUT);
        Serial.print("XSHUT pin ");
        Serial.print(xshut_pin);
        Serial.println(" configured as output");
    }
}

void Lidar_VL53L1X::resetSensor() {
    if (xshut_pin >= 0) {
        Serial.println("Performing sensor reset sequence...");
        
        // Put sensor in hardware standby
        digitalWrite(xshut_pin, LOW);
        delay(20); // Hold reset for 20ms
        
        // Release from standby and enable sensor
        digitalWrite(xshut_pin, HIGH);
        delay(200); // Wait for boot sequence (1.2ms + margin)
        
        Serial.println("Sensor reset complete");
    } else {
        Serial.println("XSHUT pin not configured - skipping reset sequence");
    }
}

float Lidar_VL53L1X::readDistance() {
    
    if (sensor.dataReady()) {
        return float(sensor.read());
    }
    
    return 0;
}

bool Lidar_VL53L1X::dataReady() {
    return sensor.dataReady();
}

VL53L1X::RangeStatus Lidar_VL53L1X::getRangeStatus() {
    return sensor.ranging_data.range_status;
}

float Lidar_VL53L1X::getPeakSignalRate() {
    return sensor.ranging_data.peak_signal_count_rate_MCPS;
}

float Lidar_VL53L1X::getAmbientRate() {
    return sensor.ranging_data.ambient_count_rate_MCPS;
}

void Lidar_VL53L1X::stopContinuous() {
    sensor.stopContinuous();
}

void Lidar_VL53L1X::startContinuous() {
    sensor.startContinuous(measurement_period);
}

uint16_t Lidar_VL53L1X::readSingle(bool blocking) {
    return sensor.readSingle(blocking);
}