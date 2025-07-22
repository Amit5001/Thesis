// generated from rosidl_generator_cpp/resource/idl__traits.hpp.em
// with input from drone_c:msg/AltitudeLidar.idl
// generated code does not contain a copyright notice

#ifndef DRONE_C__MSG__DETAIL__ALTITUDE_LIDAR__TRAITS_HPP_
#define DRONE_C__MSG__DETAIL__ALTITUDE_LIDAR__TRAITS_HPP_

#include <stdint.h>

#include <sstream>
#include <string>
#include <type_traits>

#include "drone_c/msg/detail/altitude_lidar__struct.hpp"
#include "rosidl_runtime_cpp/traits.hpp"

namespace drone_c
{

namespace msg
{

inline void to_flow_style_yaml(
  const AltitudeLidar & msg,
  std::ostream & out)
{
  out << "{";
  // member: distance
  {
    out << "distance: ";
    rosidl_generator_traits::value_to_yaml(msg.distance, out);
    out << ", ";
  }

  // member: distance_des
  {
    out << "distance_des: ";
    rosidl_generator_traits::value_to_yaml(msg.distance_des, out);
  }
  out << "}";
}  // NOLINT(readability/fn_size)

inline void to_block_style_yaml(
  const AltitudeLidar & msg,
  std::ostream & out, size_t indentation = 0)
{
  // member: distance
  {
    if (indentation > 0) {
      out << std::string(indentation, ' ');
    }
    out << "distance: ";
    rosidl_generator_traits::value_to_yaml(msg.distance, out);
    out << "\n";
  }

  // member: distance_des
  {
    if (indentation > 0) {
      out << std::string(indentation, ' ');
    }
    out << "distance_des: ";
    rosidl_generator_traits::value_to_yaml(msg.distance_des, out);
    out << "\n";
  }
}  // NOLINT(readability/fn_size)

inline std::string to_yaml(const AltitudeLidar & msg, bool use_flow_style = false)
{
  std::ostringstream out;
  if (use_flow_style) {
    to_flow_style_yaml(msg, out);
  } else {
    to_block_style_yaml(msg, out);
  }
  return out.str();
}

}  // namespace msg

}  // namespace drone_c

namespace rosidl_generator_traits
{

[[deprecated("use drone_c::msg::to_block_style_yaml() instead")]]
inline void to_yaml(
  const drone_c::msg::AltitudeLidar & msg,
  std::ostream & out, size_t indentation = 0)
{
  drone_c::msg::to_block_style_yaml(msg, out, indentation);
}

[[deprecated("use drone_c::msg::to_yaml() instead")]]
inline std::string to_yaml(const drone_c::msg::AltitudeLidar & msg)
{
  return drone_c::msg::to_yaml(msg);
}

template<>
inline const char * data_type<drone_c::msg::AltitudeLidar>()
{
  return "drone_c::msg::AltitudeLidar";
}

template<>
inline const char * name<drone_c::msg::AltitudeLidar>()
{
  return "drone_c/msg/AltitudeLidar";
}

template<>
struct has_fixed_size<drone_c::msg::AltitudeLidar>
  : std::integral_constant<bool, true> {};

template<>
struct has_bounded_size<drone_c::msg::AltitudeLidar>
  : std::integral_constant<bool, true> {};

template<>
struct is_message<drone_c::msg::AltitudeLidar>
  : std::true_type {};

}  // namespace rosidl_generator_traits

#endif  // DRONE_C__MSG__DETAIL__ALTITUDE_LIDAR__TRAITS_HPP_
