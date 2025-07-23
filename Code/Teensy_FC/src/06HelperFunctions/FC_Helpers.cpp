#include "FC_Helpers.h"
#include "PID_type.h"
#include "EkfClass.h"

static int prev_mode = 1;  // To track the previous mode for ALTHOLD transition

namespace FC_Helpers {
    
    void updateController(AlfredoCRSF& ELRS, Controller_s& controller_data) {
        // Update the controller data:
        ELRS.update();
        
        controller_data.throttle = ELRS.getChannel(3);
        controller_data.roll = ELRS.getChannel(1);
        controller_data.pitch = ELRS.getChannel(2);
        controller_data.yaw = ELRS.getChannel(4);
        controller_data.aux1 = ELRS.getChannel(9);
        controller_data.aux2 = ELRS.getChannel(6);
        controller_data.aux3 = ELRS.getChannel(7);
        controller_data.aux4 = ELRS.getChannel(8);
    }
    
    void controllerThreshold(Controller_s& controller_data) {
        if ((controller_data.roll <= CONTROLL_THR_MAX) && (controller_data.roll >= CONTROLL_THR_MIN)) {
            controller_data.roll = 1500;
        }
        if ((controller_data.pitch <= CONTROLL_THR_MAX) && (controller_data.pitch >= CONTROLL_THR_MIN)) {
            controller_data.pitch = 1500;
        }
        if ((controller_data.yaw <= CONTROLL_THR_MAX) && (controller_data.yaw >= CONTROLL_THR_MIN)) {
            controller_data.yaw = 1500;
        }
    }
    
    void mappingController(Controller_s& controller_data, Drone_Data_t& drone_data_header, 
                          attitude_t& desired_attitude, attitude_t& desired_rate, Measurement_t& meas, Altitude_t& altitude_data) {
        controllerThreshold(controller_data);        
        switch (drone_data_header.drone_mode) {
            case DroneMode::MODE_STABILIZE:
                if (prev_mode == int(DroneMode::MODE_ALTHOLD)) {
                    // Reset desired altitude when switching from ALTHOLD to RATE mode
                    Reset_PID();
                }
                desired_attitude.roll = map(controller_data.roll, CONTROLLER_MIN, CONTROLLER_MAX, -MAX_ANGLE, MAX_ANGLE);
                desired_attitude.pitch = map(controller_data.pitch, CONTROLLER_MIN, CONTROLLER_MAX, MAX_ANGLE, -MAX_ANGLE);
                desired_attitude.yaw = map(controller_data.yaw, CONTROLLER_MIN, CONTROLLER_MAX, MAX_ANGLE, -MAX_ANGLE);
                break;
                
            case DroneMode::MODE_RATE:
                if (prev_mode == int(DroneMode::MODE_ALTHOLD)) {
                    // Reset desired altitude when switching from ALTHOLD to RATE mode
                    Reset_PID();
                }
                desired_rate.roll = map(controller_data.roll, CONTROLLER_MIN, CONTROLLER_MAX, -MAX_RATE, MAX_RATE);
                desired_rate.pitch = map(controller_data.pitch, CONTROLLER_MIN, CONTROLLER_MAX, -MAX_RATE, MAX_RATE);
                desired_rate.yaw = map(controller_data.yaw, CONTROLLER_MIN, CONTROLLER_MAX, MAX_RATE, -MAX_RATE);
                break;
                
            case DroneMode::MODE_ALTHOLD:
                // This part is the same as Stabilize mode
                desired_attitude.roll = map(controller_data.roll, CONTROLLER_MIN, CONTROLLER_MAX, -MAX_ANGLE, MAX_ANGLE);
                desired_attitude.pitch = map(controller_data.pitch, CONTROLLER_MIN, CONTROLLER_MAX, MAX_ANGLE, -MAX_ANGLE);
                desired_attitude.yaw = map(controller_data.yaw, CONTROLLER_MIN, CONTROLLER_MAX, MAX_ANGLE, -MAX_ANGLE);
                
                // This is the new part for Alt-Hold
                if (prev_mode != int(DroneMode::MODE_ALTHOLD)) {
                    // First time entering ALTHOLD mode - set current altitude as desired
                    altitude_data.desired_altitude = altitude_data.current_altitude;

                }

                // Rate-based altitude control
                const int THROTTLE_CENTER = 1500;
                const int DEADZONE = 100;  // Larger deadzone for stability
                const float MAX_ALTITUDE_RATE = 0.5f;  // Max 0.5m/s altitude change rate
                
                float altitude_rate = 0.0f;
                
                if (controller_data.throttle > (THROTTLE_CENTER + DEADZONE)) {
                    // Map throttle to positive altitude rate
                    altitude_rate = map(controller_data.throttle, THROTTLE_CENTER + DEADZONE, CONTROLLER_MAX, 
                                    0, MAX_ALTITUDE_RATE * 1000) / 1000.0f;
                } 
                else if (controller_data.throttle < (THROTTLE_CENTER - DEADZONE)) {
                    // Map throttle to negative altitude rate
                    altitude_rate = -map(controller_data.throttle, CONTROLLER_MIN, THROTTLE_CENTER - DEADZONE, 
                                        MAX_ALTITUDE_RATE * 1000, 0) / 1000.0f;
                }
                
                altitude_data.desired_altitude += altitude_rate * (alt_DT);  // actual_dt should be your loop time
                
                // Clamp altitude limits
                if (altitude_data.desired_altitude < 0.0f) {
                    altitude_data.desired_altitude = 0.0f;
                }
                if (altitude_data.desired_altitude > 3.0f) {
                    altitude_data.desired_altitude = 3.0f;
                }            
                break;
        }
        prev_mode = int(drone_data_header.drone_mode);  // Update previous mode
    }
    
    void resetMicrocontroller(Controller_s& controller_data) {
        if (controller_data.aux3 > 1700) {
            Serial.println(" reset ");
            SCB_AIRCR = 0x05FA0004;
        }
    }
    
    void checkArmingState(Controller_s& controller_data, Drone_Data_t& drone_data_header, 
                         Motors& motors) {
        if (controller_data.aux2 > 1500) {  // Switch is in high position
            if (controller_data.throttle < (MOTOR_START + 100)) {
                drone_data_header.is_armed = true;
            }
        } else {  // Switch is in low position
            drone_data_header.is_armed = false;
            motors.Disarm();  // Ensure motors are stopped when disarmed
            Reset_PID();      // Reset PID states when disarmed
            resetMicrocontroller(controller_data);
        }
    }
    
    void channelEstimated(Controller_s& controller_data, Drone_Data_t& drone_data_header) {
        if (controller_data.aux4 > 1700) {
            drone_data_header.filter_mode = DroneFilter::KALMAN;
        } else {
            drone_data_header.filter_mode = DroneFilter::COMPCLASS;
        }
    }
    
    void estimatedStateMethod(Drone_Data_t& drone_data_header, EKF& ekf, CompFilter& comp_filter,
                             Measurement_t& meas, attitude_t& estimated_attitude, quat_t& q_est) {
        // Note: This function needs controller_data parameter to work properly
        // For now, commenting out the problematic line
        // channelEstimated(controller_data, drone_data_header);
        
        switch (drone_data_header.filter_mode) {
            case DroneFilter::KALMAN:
                ekf.run_kalman(&estimated_attitude, &q_est);
                break;
                
            case DroneFilter::COMPCLASS:
                comp_filter.UpdateQ(&meas.gyroRAD, &meas.acc, DT);
                comp_filter.GetEulerRPYdeg(&estimated_attitude);
                comp_filter.GetQuaternion(&q_est);  
                break;
                
            default:
                ekf.run_kalman(&estimated_attitude, &q_est);
                break;
        }
    }
    
    void checkMode(Controller_s& controller_data, Drone_Data_t& drone_data_header) {
        if (controller_data.aux1 == 1503) {
            drone_data_header.drone_mode = DroneMode::MODE_STABILIZE;
        }
        else if (controller_data.aux1 == 2000) {
            drone_data_header.drone_mode = DroneMode::MODE_ALTHOLD;
        }
        else {
            drone_data_header.drone_mode = DroneMode::MODE_RATE;
        }
    }
    
    void stabilizeLoop(elapsedMicros& stab_timer, Controller_s& controller_data, 
                      Drone_Data_t& drone_data_header, attitude_t& desired_attitude,
                      attitude_t& estimated_attitude, attitude_t& desired_rate, PID_out_t& PID_stab_out,
                      Measurement_t& meas) {  // Added meas parameter
        if (stab_timer >= STAB_PERIOD) {
            double t_PID_s = (double)stab_timer / 1000000.0f;
            PID_stab_out = PID_stab(desired_attitude, estimated_attitude, t_PID_s);
            PID_stab_out.PID_ret.pitch = -1 * PID_stab_out.PID_ret.pitch;
            desired_rate = PID_stab_out.PID_ret;
            desired_rate.yaw = map(controller_data.yaw, CONTROLLER_MIN, CONTROLLER_MAX, MAX_RATE, -MAX_RATE);
            stab_timer = 0;
        }
    }
}