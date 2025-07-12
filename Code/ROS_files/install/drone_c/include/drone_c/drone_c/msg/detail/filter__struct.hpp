// generated from rosidl_generator_cpp/resource/idl__struct.hpp.em
// with input from drone_c:msg/Filter.idl
// generated code does not contain a copyright notice

#ifndef DRONE_C__MSG__DETAIL__FILTER__STRUCT_HPP_
#define DRONE_C__MSG__DETAIL__FILTER__STRUCT_HPP_

#include <algorithm>
#include <array>
#include <memory>
#include <string>
#include <vector>

#include "rosidl_runtime_cpp/bounded_vector.hpp"
#include "rosidl_runtime_cpp/message_initialization.hpp"


#ifndef _WIN32
# define DEPRECATED__drone_c__msg__Filter __attribute__((deprecated))
#else
# define DEPRECATED__drone_c__msg__Filter __declspec(deprecated)
#endif

namespace drone_c
{

namespace msg
{

// message struct
template<class ContainerAllocator>
struct Filter_
{
  using Type = Filter_<ContainerAllocator>;

  explicit Filter_(rosidl_runtime_cpp::MessageInitialization _init = rosidl_runtime_cpp::MessageInitialization::ALL)
  {
    if (rosidl_runtime_cpp::MessageInitialization::ALL == _init ||
      rosidl_runtime_cpp::MessageInitialization::ZERO == _init)
    {
      this->std_beta = 0.0f;
      this->high_beta = 0.0f;
      this->low_beta = 0.0f;
    }
  }

  explicit Filter_(const ContainerAllocator & _alloc, rosidl_runtime_cpp::MessageInitialization _init = rosidl_runtime_cpp::MessageInitialization::ALL)
  {
    (void)_alloc;
    if (rosidl_runtime_cpp::MessageInitialization::ALL == _init ||
      rosidl_runtime_cpp::MessageInitialization::ZERO == _init)
    {
      this->std_beta = 0.0f;
      this->high_beta = 0.0f;
      this->low_beta = 0.0f;
    }
  }

  // field types and members
  using _std_beta_type =
    float;
  _std_beta_type std_beta;
  using _high_beta_type =
    float;
  _high_beta_type high_beta;
  using _low_beta_type =
    float;
  _low_beta_type low_beta;

  // setters for named parameter idiom
  Type & set__std_beta(
    const float & _arg)
  {
    this->std_beta = _arg;
    return *this;
  }
  Type & set__high_beta(
    const float & _arg)
  {
    this->high_beta = _arg;
    return *this;
  }
  Type & set__low_beta(
    const float & _arg)
  {
    this->low_beta = _arg;
    return *this;
  }

  // constant declarations

  // pointer types
  using RawPtr =
    drone_c::msg::Filter_<ContainerAllocator> *;
  using ConstRawPtr =
    const drone_c::msg::Filter_<ContainerAllocator> *;
  using SharedPtr =
    std::shared_ptr<drone_c::msg::Filter_<ContainerAllocator>>;
  using ConstSharedPtr =
    std::shared_ptr<drone_c::msg::Filter_<ContainerAllocator> const>;

  template<typename Deleter = std::default_delete<
      drone_c::msg::Filter_<ContainerAllocator>>>
  using UniquePtrWithDeleter =
    std::unique_ptr<drone_c::msg::Filter_<ContainerAllocator>, Deleter>;

  using UniquePtr = UniquePtrWithDeleter<>;

  template<typename Deleter = std::default_delete<
      drone_c::msg::Filter_<ContainerAllocator>>>
  using ConstUniquePtrWithDeleter =
    std::unique_ptr<drone_c::msg::Filter_<ContainerAllocator> const, Deleter>;
  using ConstUniquePtr = ConstUniquePtrWithDeleter<>;

  using WeakPtr =
    std::weak_ptr<drone_c::msg::Filter_<ContainerAllocator>>;
  using ConstWeakPtr =
    std::weak_ptr<drone_c::msg::Filter_<ContainerAllocator> const>;

  // pointer types similar to ROS 1, use SharedPtr / ConstSharedPtr instead
  // NOTE: Can't use 'using' here because GNU C++ can't parse attributes properly
  typedef DEPRECATED__drone_c__msg__Filter
    std::shared_ptr<drone_c::msg::Filter_<ContainerAllocator>>
    Ptr;
  typedef DEPRECATED__drone_c__msg__Filter
    std::shared_ptr<drone_c::msg::Filter_<ContainerAllocator> const>
    ConstPtr;

  // comparison operators
  bool operator==(const Filter_ & other) const
  {
    if (this->std_beta != other.std_beta) {
      return false;
    }
    if (this->high_beta != other.high_beta) {
      return false;
    }
    if (this->low_beta != other.low_beta) {
      return false;
    }
    return true;
  }
  bool operator!=(const Filter_ & other) const
  {
    return !this->operator==(other);
  }
};  // struct Filter_

// alias to use template instance with default allocator
using Filter =
  drone_c::msg::Filter_<std::allocator<void>>;

// constant definitions

}  // namespace msg

}  // namespace drone_c

#endif  // DRONE_C__MSG__DETAIL__FILTER__STRUCT_HPP_
