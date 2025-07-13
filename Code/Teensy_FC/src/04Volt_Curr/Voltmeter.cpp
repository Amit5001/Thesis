#include "Voltmeter.h"

Voltmeter::Voltmeter(Drone_Data_t *drone_data ,int voltmeterPin, int currentPin , float voltmeter_calibration_factor, float current_calibration_factor, float current_bias) {
    _drone_data = drone_data;
    _voltmeterPin = voltmeterPin;
    _currentPin = currentPin;
    _voltmeter_calibration_factor = voltmeter_calibration_factor;
    _current_calibration_factor = current_calibration_factor;
    _current_bias = current_bias;
}

void Voltmeter::read_bat_data() {
    analogReadResolution(12);  // Set the resolution to 12 bits
    
    _drone_data->voltage_reading = (float)analogRead(_voltmeterPin) / _voltmeter_calibration_factor;
    // Serial.println(_drone_data->voltage_reading);
    _drone_data->current_reading = (((float)analogRead(_currentPin)/4096.0) * 3.3)/ _current_calibration_factor + _current_bias;
    // Serial.println(_drone_data->current_reading);
}