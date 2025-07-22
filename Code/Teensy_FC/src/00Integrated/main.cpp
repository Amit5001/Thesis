#include <Arduino.h>
#include "Wire.h"
#include "CompClass.h"
#include "IMU_type.h"
#include <AlfredoCRSF.h>
#include "MotorsControl.h"
#include "PID_type.h"
#include "EkfClass.h"
#include "STD_Filter.h"
#include "drone_comclass.h"
#include "Voltmeter.h"
#include "Var_types.h"
#include "drone_identify.h"
#include "Lidar_VL53L1X.h"
#include "FC_Helpers.h"  // Your new header file

/*
------------------------------------------ Global Variables ------------------------------------------
*/

// ELRS Controller:
AlfredoCRSF ELRS;
Controller_s controller_data;

// Motors Variables:
Motors motors(MOTOR1_PIN, MOTOR2_PIN, MOTOR3_PIN, MOTOR4_PIN);

// LiDAR Configuration
bool io_2v8 = false;
static const uint16_t TimingBudget = 33000;
static const uint16_t Timeout = 500;
static const uint16_t Period = 33;
uint8_t xshut_pin = 26;
Lidar_VL53L1X lidar(io_2v8, VL53L1X::Long, TimingBudget, Period, Timeout, xshut_pin, Wire2);
float lidar_distance = 0;
int thrust = 0;

// All your other global variables...
Measurement_t meas;
IMU_Func imu(&meas, SAMPLE_RATE);
drone_tune_t drone_tune;
CompFilter comp_filter(&drone_tune.filter_data); 
quat_t q_est;
attitude_t desired_attitude;
motor_t motor_pwm;
attitude_t desired_rate;
attitude_t estimated_attitude;
attitude_t estimated_rate;
Altitude_t altitude_data;
PID_out_t PID_stab_out;
PID_out_t PID_rate_out;
Drone_Data_t drone_data_header;
Voltmeter voltmeter(&drone_data_header, A3, A2);
Drone_com drone_com(&meas, &q_est, &desired_attitude, &motor_pwm,
                    &desired_rate, &estimated_attitude, &estimated_rate, &PID_stab_out, &PID_rate_out,
                    &controller_data, &drone_tune, &drone_data_header, &comp_filter, &altitude_data);

// Timers
elapsedMicros motor_timer;
elapsedMicros stab_timer;
elapsedMicros imu_timer;
elapsedMicros send_data_timer;
elapsedMicros estimated_filter_timer;
elapsedMicros lidar_meas_timer;
elapsedMicros alt_PID_timer;

// Other objects
EKF ekf(&meas, 1 / SAMPLE_RATE);
STD_Filter std_filter(&meas, SAMPLE_RATE);

double t_PID_s = 0.0f;
double t_PID_r = 0.0f;
float actual_dt = 0.0f;

void setup() {
    Serial.begin(115200);
    drone_com.init_com();
    getbot_param(drone_tune, drone_data_header);
    imu.init_IMU(drone_data_header.acc_offset);
    voltmeter.init_voltmeter();

    ELRSSerial.begin(CRSF_BAUDRATE, SERIAL_8N1);
    if (!ELRSSerial) {
        while (1) {
            Serial.println("Invalid ELRSSerial configuration");
        }
    }

    // Initialize the LiDAR sensor
    if (!lidar.init_Lidar()) {
        Serial.println("Failed to initialize LiDAR sensor");
    } else {
        Serial.println("LiDAR sensor initialized successfully");
    }

    ELRS.begin(ELRSSerial);
    setPID_params(&drone_tune.pid_const);
    comp_filter.set_beta(&drone_tune.filter_data);
    // imu.Initial_Calibration();
    motors.Motors_init();
}

void loop() {
    // Update ELRS data using namespace function
    FC_Helpers::updateController(ELRS, controller_data);
    FC_Helpers::checkArmingState(controller_data, drone_data_header, motors);
    FC_Helpers::checkMode(controller_data, drone_data_header);

    if (imu_timer >= IMU_PERIOD) {
        actual_dt = (double)imu_timer / 1000000.0f;
        imu.Read_IMU();
        std_filter.all_filter();
        FC_Helpers::estimatedStateMethod(drone_data_header, ekf, comp_filter, meas, estimated_attitude, q_est);
        voltmeter.read_bat_data();
        FC_Helpers::mappingController(controller_data, drone_data_header, desired_attitude, desired_rate, meas, altitude_data);
        // Serial.println(altitude_data.desired_altitude);

        if (lidar_meas_timer >= ALT_PERIOD) {
            altitude_data.current_altitude = lidar.readDistance() / 1000.0f;
            lidar_meas_timer = 0;
        }

        if (drone_data_header.is_armed) {
            estimated_rate.roll = meas.gyroDEG.x;
            estimated_rate.pitch = meas.gyroDEG.y;
            estimated_rate.yaw = meas.gyroDEG.z;
            thrust = controller_data.throttle;
            
            switch(drone_data_header.drone_mode) {
                case DroneMode::MODE_RATE:
                    // Serial.println("Rate Mode");
                    estimated_rate.roll = meas.gyroDEG.x;
                    estimated_rate.pitch = meas.gyroDEG.y;
                    estimated_rate.yaw = meas.gyroDEG.z;
                    break;
                    
                case DroneMode::MODE_STABILIZE:
                    // Serial.println("Stabilize Mode");
                    FC_Helpers::stabilizeLoop(stab_timer, controller_data, drone_data_header, 
                                            desired_attitude, estimated_attitude, desired_rate, PID_stab_out, meas);
                    break;
                    
                case DroneMode::MODE_ALTHOLD:
                    // Serial.println("Alt-Hold Mode");
                    FC_Helpers::stabilizeLoop(stab_timer, controller_data, drone_data_header, 
                                                  desired_attitude, estimated_attitude, desired_rate, PID_stab_out, meas);
                    if (alt_PID_timer >= ALT_PERIOD) {
                        thrust = Altitude_Controller(&altitude_data, drone_data_header.current_reading);
                        thrust = constrain(thrust, 1100, 1900);  // Constrain thrust to a safe range
                        alt_PID_timer = 0;
                    }
                    Serial.println(thrust);
                    break;
            }

            if ((controller_data.throttle > 1000) && (motor_timer >= MOTOR_PERIOD)) {
                t_PID_r = (float)motor_timer / 1000000.0f;
                PID_rate_out = PID_rate(desired_rate, estimated_rate, t_PID_r);
                // Serial.println(thrust);
                motors.Motor_Mix(PID_rate_out.PID_ret, thrust);
                motors.set_motorPWM();
                motor_timer = 0;
            }

            motor_pwm = motors.Get_motor();
        }

        if (send_data_timer >= SEND_DATA_PERIOD) {
            drone_com.convert_Measurment_to_byte();
            drone_com.send_data();
            send_data_timer = 0;
        }
        imu_timer = 0;
    }
}