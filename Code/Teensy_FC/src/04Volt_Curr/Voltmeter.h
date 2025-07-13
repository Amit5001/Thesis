#ifndef VOLTMETER_H
#define VOLTMETER_H

#include "Arduino.h"
#include "Var_types.h"

class Voltmeter {
    public:
        Voltmeter(Drone_Data_t *drone_data ,int voltmeterPin, int currentPin , float voltmeter_calibration_factor, float current_calibration_factor, float current_bias = 0.0f);
        void read_bat_data();
    private:
        Drone_Data_t *_drone_data;
        int _voltmeterPin;
        int _currentPin;
        float _voltmeter_calibration_factor;
        float _current_calibration_factor;
        float _current_bias;

};
#endif
