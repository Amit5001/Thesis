// generated from rosidl_generator_cpp/resource/idl__builder.hpp.em
// with input from drone_c:msg/AltitudeLidar.idl
// generated code does not contain a copyright notice

#ifndef DRONE_C__MSG__DETAIL__ALTITUDE_LIDAR__BUILDER_HPP_
#define DRONE_C__MSG__DETAIL__ALTITUDE_LIDAR__BUILDER_HPP_

#include <algorithm>
#include <utility>

#include "drone_c/msg/detail/altitude_lidar__struct.hpp"
#include "rosidl_runtime_cpp/message_initialization.hpp"


namespace drone_c
{

namespace msg
{

namespace builder
{

class Init_AltitudeLidar_distance
{
public:
  Init_AltitudeLidar_distance()
  : msg_(::rosidl_runtime_cpp::MessageInitialization::SKIP)
  {}
  ::drone_c::msg::AltitudeLidar distance(::drone_c::msg::AltitudeLidar::_distance_type arg)
  {
    msg_.distance = std::move(arg);
    return std::move(msg_);
  }

private:
  ::drone_c::msg::AltitudeLidar msg_;
};

}  // namespace builder

}  // namespace msg

template<typename MessageType>
auto build();

template<>
inline
auto build<::drone_c::msg::AltitudeLidar>()
{
  return drone_c::msg::builder::Init_AltitudeLidar_distance();
}

}  // namespace drone_c

#endif  // DRONE_C__MSG__DETAIL__ALTITUDE_LIDAR__BUILDER_HPP_
