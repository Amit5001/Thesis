#ifndef FC_HELPERS_H
#define FC_HELPERS_H
#include "Var_types.h"
#include "drone_comclass.h"
#include "MotorsControl.h"
#include <AlfredoCRSF.h>
#include "EkfClass.h"


namespace FC_Helpers {
    // Controller functions
    void updateController(AlfredoCRSF& ELRS, Controller_s& controller_data);
    void controllerThreshold(Controller_s& controller_data);
    void mappingController(Controller_s& controller_data, Drone_Data_t& drone_data_header,
                          attitude_t& desired_attitude, attitude_t& desired_rate, Measurement_t& meas, Altitude_t& altitude_data);
    
    // System control functions
    void checkArmingState(Controller_s& controller_data, Drone_Data_t& drone_data_header,
                         Motors& motors);
    void resetMicrocontroller(Controller_s& controller_data);
    void checkMode(Controller_s& controller_data, Drone_Data_t& drone_data_header);
    
    // State estimation functions
    void channelEstimated(Controller_s& controller_data, Drone_Data_t& drone_data_header);
    void estimatedStateMethod(Drone_Data_t& drone_data_header, EKF& ekf, CompFilter& comp_filter,
                             Measurement_t& meas, attitude_t& estimated_attitude, quat_t& q_est);
    
    // Flight control loops
    void stabilizeLoop(elapsedMicros& stab_timer, Controller_s& controller_data,
                      Drone_Data_t& drone_data_header, attitude_t& desired_attitude,
                      attitude_t& estimated_attitude, attitude_t& desired_rate, PID_out_t& PID_stab_out,
                      Measurement_t& meas);  // Added meas parameter
}
#endif // FC_HELPERS_H