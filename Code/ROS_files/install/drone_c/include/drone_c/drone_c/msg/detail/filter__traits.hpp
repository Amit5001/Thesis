// generated from rosidl_generator_cpp/resource/idl__traits.hpp.em
// with input from drone_c:msg/Filter.idl
// generated code does not contain a copyright notice

#ifndef DRONE_C__MSG__DETAIL__FILTER__TRAITS_HPP_
#define DRONE_C__MSG__DETAIL__FILTER__TRAITS_HPP_

#include <stdint.h>

#include <sstream>
#include <string>
#include <type_traits>

#include "drone_c/msg/detail/filter__struct.hpp"
#include "rosidl_runtime_cpp/traits.hpp"

namespace drone_c
{

namespace msg
{

inline void to_flow_style_yaml(
  const Filter & msg,
  std::ostream & out)
{
  out << "{";
  // member: std_beta
  {
    out << "std_beta: ";
    rosidl_generator_traits::value_to_yaml(msg.std_beta, out);
    out << ", ";
  }

  // member: high_beta
  {
    out << "high_beta: ";
    rosidl_generator_traits::value_to_yaml(msg.high_beta, out);
    out << ", ";
  }

  // member: low_beta
  {
    out << "low_beta: ";
    rosidl_generator_traits::value_to_yaml(msg.low_beta, out);
  }
  out << "}";
}  // NOLINT(readability/fn_size)

inline void to_block_style_yaml(
  const Filter & msg,
  std::ostream & out, size_t indentation = 0)
{
  // member: std_beta
  {
    if (indentation > 0) {
      out << std::string(indentation, ' ');
    }
    out << "std_beta: ";
    rosidl_generator_traits::value_to_yaml(msg.std_beta, out);
    out << "\n";
  }

  // member: high_beta
  {
    if (indentation > 0) {
      out << std::string(indentation, ' ');
    }
    out << "high_beta: ";
    rosidl_generator_traits::value_to_yaml(msg.high_beta, out);
    out << "\n";
  }

  // member: low_beta
  {
    if (indentation > 0) {
      out << std::string(indentation, ' ');
    }
    out << "low_beta: ";
    rosidl_generator_traits::value_to_yaml(msg.low_beta, out);
    out << "\n";
  }
}  // NOLINT(readability/fn_size)

inline std::string to_yaml(const Filter & msg, bool use_flow_style = false)
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
  const drone_c::msg::Filter & msg,
  std::ostream & out, size_t indentation = 0)
{
  drone_c::msg::to_block_style_yaml(msg, out, indentation);
}

[[deprecated("use drone_c::msg::to_yaml() instead")]]
inline std::string to_yaml(const drone_c::msg::Filter & msg)
{
  return drone_c::msg::to_yaml(msg);
}

template<>
inline const char * data_type<drone_c::msg::Filter>()
{
  return "drone_c::msg::Filter";
}

template<>
inline const char * name<drone_c::msg::Filter>()
{
  return "drone_c/msg/Filter";
}

template<>
struct has_fixed_size<drone_c::msg::Filter>
  : std::integral_constant<bool, true> {};

template<>
struct has_bounded_size<drone_c::msg::Filter>
  : std::integral_constant<bool, true> {};

template<>
struct is_message<drone_c::msg::Filter>
  : std::true_type {};

}  // namespace rosidl_generator_traits

#endif  // DRONE_C__MSG__DETAIL__FILTER__TRAITS_HPP_
