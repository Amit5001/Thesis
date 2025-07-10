// generated from rosidl_generator_cpp/resource/idl__builder.hpp.em
// with input from drone_c:msg/Filter.idl
// generated code does not contain a copyright notice

#ifndef DRONE_C__MSG__DETAIL__FILTER__BUILDER_HPP_
#define DRONE_C__MSG__DETAIL__FILTER__BUILDER_HPP_

#include <algorithm>
#include <utility>

#include "drone_c/msg/detail/filter__struct.hpp"
#include "rosidl_runtime_cpp/message_initialization.hpp"


namespace drone_c
{

namespace msg
{

namespace builder
{

class Init_Filter_low_beta
{
public:
  explicit Init_Filter_low_beta(::drone_c::msg::Filter & msg)
  : msg_(msg)
  {}
  ::drone_c::msg::Filter low_beta(::drone_c::msg::Filter::_low_beta_type arg)
  {
    msg_.low_beta = std::move(arg);
    return std::move(msg_);
  }

private:
  ::drone_c::msg::Filter msg_;
};

class Init_Filter_high_beta
{
public:
  explicit Init_Filter_high_beta(::drone_c::msg::Filter & msg)
  : msg_(msg)
  {}
  Init_Filter_low_beta high_beta(::drone_c::msg::Filter::_high_beta_type arg)
  {
    msg_.high_beta = std::move(arg);
    return Init_Filter_low_beta(msg_);
  }

private:
  ::drone_c::msg::Filter msg_;
};

class Init_Filter_std_beta
{
public:
  Init_Filter_std_beta()
  : msg_(::rosidl_runtime_cpp::MessageInitialization::SKIP)
  {}
  Init_Filter_high_beta std_beta(::drone_c::msg::Filter::_std_beta_type arg)
  {
    msg_.std_beta = std::move(arg);
    return Init_Filter_high_beta(msg_);
  }

private:
  ::drone_c::msg::Filter msg_;
};

}  // namespace builder

}  // namespace msg

template<typename MessageType>
auto build();

template<>
inline
auto build<::drone_c::msg::Filter>()
{
  return drone_c::msg::builder::Init_Filter_std_beta();
}

}  // namespace drone_c

#endif  // DRONE_C__MSG__DETAIL__FILTER__BUILDER_HPP_
