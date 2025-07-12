// generated from rosidl_generator_cpp/resource/idl__struct.hpp.em
// with input from drone_c:msg/AltitudeLidar.idl
// generated code does not contain a copyright notice

#ifndef DRONE_C__MSG__DETAIL__ALTITUDE_LIDAR__STRUCT_HPP_
#define DRONE_C__MSG__DETAIL__ALTITUDE_LIDAR__STRUCT_HPP_

#include <algorithm>
#include <array>
#include <memory>
#include <string>
#include <vector>

#include "rosidl_runtime_cpp/bounded_vector.hpp"
#include "rosidl_runtime_cpp/message_initialization.hpp"


#ifndef _WIN32
# define DEPRECATED__drone_c__msg__AltitudeLidar __attribute__((deprecated))
#else
# define DEPRECATED__drone_c__msg__AltitudeLidar __declspec(deprecated)
#endif

namespace drone_c
{

namespace msg
{

// message struct
template<class ContainerAllocator>
struct AltitudeLidar_
{
  using Type = AltitudeLidar_<ContainerAllocator>;

  explicit AltitudeLidar_(rosidl_runtime_cpp::MessageInitialization _init = rosidl_runtime_cpp::MessageInitialization::ALL)
  {
    if (rosidl_runtime_cpp::MessageInitialization::ALL == _init ||
      rosidl_runtime_cpp::MessageInitialization::ZERO == _init)
    {
      this->distance = 0.0f;
    }
  }

  explicit AltitudeLidar_(const ContainerAllocator & _alloc, rosidl_runtime_cpp::MessageInitialization _init = rosidl_runtime_cpp::MessageInitialization::ALL)
  {
    (void)_alloc;
    if (rosidl_runtime_cpp::MessageInitialization::ALL == _init ||
      rosidl_runtime_cpp::MessageInitialization::ZERO == _init)
    {
      this->distance = 0.0f;
    }
  }

  // field types and members
  using _distance_type =
    float;
  _distance_type distance;

  // setters for named parameter idiom
  Type & set__distance(
    const float & _arg)
  {
    this->distance = _arg;
    return *this;
  }

  // constant declarations

  // pointer types
  using RawPtr =
    drone_c::msg::AltitudeLidar_<ContainerAllocator> *;
  using ConstRawPtr =
    const drone_c::msg::AltitudeLidar_<ContainerAllocator> *;
  using SharedPtr =
    std::shared_ptr<drone_c::msg::AltitudeLidar_<ContainerAllocator>>;
  using ConstSharedPtr =
    std::shared_ptr<drone_c::msg::AltitudeLidar_<ContainerAllocator> const>;

  template<typename Deleter = std::default_delete<
      drone_c::msg::AltitudeLidar_<ContainerAllocator>>>
  using UniquePtrWithDeleter =
    std::unique_ptr<drone_c::msg::AltitudeLidar_<ContainerAllocator>, Deleter>;

  using UniquePtr = UniquePtrWithDeleter<>;

  template<typename Deleter = std::default_delete<
      drone_c::msg::AltitudeLidar_<ContainerAllocator>>>
  using ConstUniquePtrWithDeleter =
    std::unique_ptr<drone_c::msg::AltitudeLidar_<ContainerAllocator> const, Deleter>;
  using ConstUniquePtr = ConstUniquePtrWithDeleter<>;

  using WeakPtr =
    std::weak_ptr<drone_c::msg::AltitudeLidar_<ContainerAllocator>>;
  using ConstWeakPtr =
    std::weak_ptr<drone_c::msg::AltitudeLidar_<ContainerAllocator> const>;

  // pointer types similar to ROS 1, use SharedPtr / ConstSharedPtr instead
  // NOTE: Can't use 'using' here because GNU C++ can't parse attributes properly
  typedef DEPRECATED__drone_c__msg__AltitudeLidar
    std::shared_ptr<drone_c::msg::AltitudeLidar_<ContainerAllocator>>
    Ptr;
  typedef DEPRECATED__drone_c__msg__AltitudeLidar
    std::shared_ptr<drone_c::msg::AltitudeLidar_<ContainerAllocator> const>
    ConstPtr;

  // comparison operators
  bool operator==(const AltitudeLidar_ & other) const
  {
    if (this->distance != other.distance) {
      return false;
    }
    return true;
  }
  bool operator!=(const AltitudeLidar_ & other) const
  {
    return !this->operator==(other);
  }
};  // struct AltitudeLidar_

// alias to use template instance with default allocator
using AltitudeLidar =
  drone_c::msg::AltitudeLidar_<std::allocator<void>>;

// constant definitions

}  // namespace msg

}  // namespace drone_c

#endif  // DRONE_C__MSG__DETAIL__ALTITUDE_LIDAR__STRUCT_HPP_
