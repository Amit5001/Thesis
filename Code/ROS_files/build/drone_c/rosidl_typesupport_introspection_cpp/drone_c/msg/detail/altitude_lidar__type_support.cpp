// generated from rosidl_typesupport_introspection_cpp/resource/idl__type_support.cpp.em
// with input from drone_c:msg/AltitudeLidar.idl
// generated code does not contain a copyright notice

#include "array"
#include "cstddef"
#include "string"
#include "vector"
#include "rosidl_runtime_c/message_type_support_struct.h"
#include "rosidl_typesupport_cpp/message_type_support.hpp"
#include "rosidl_typesupport_interface/macros.h"
#include "drone_c/msg/detail/altitude_lidar__struct.hpp"
#include "rosidl_typesupport_introspection_cpp/field_types.hpp"
#include "rosidl_typesupport_introspection_cpp/identifier.hpp"
#include "rosidl_typesupport_introspection_cpp/message_introspection.hpp"
#include "rosidl_typesupport_introspection_cpp/message_type_support_decl.hpp"
#include "rosidl_typesupport_introspection_cpp/visibility_control.h"

namespace drone_c
{

namespace msg
{

namespace rosidl_typesupport_introspection_cpp
{

void AltitudeLidar_init_function(
  void * message_memory, rosidl_runtime_cpp::MessageInitialization _init)
{
  new (message_memory) drone_c::msg::AltitudeLidar(_init);
}

void AltitudeLidar_fini_function(void * message_memory)
{
  auto typed_message = static_cast<drone_c::msg::AltitudeLidar *>(message_memory);
  typed_message->~AltitudeLidar();
}

static const ::rosidl_typesupport_introspection_cpp::MessageMember AltitudeLidar_message_member_array[2] = {
  {
    "distance",  // name
    ::rosidl_typesupport_introspection_cpp::ROS_TYPE_FLOAT,  // type
    0,  // upper bound of string
    nullptr,  // members of sub message
    false,  // is array
    0,  // array size
    false,  // is upper bound
    offsetof(drone_c::msg::AltitudeLidar, distance),  // bytes offset in struct
    nullptr,  // default value
    nullptr,  // size() function pointer
    nullptr,  // get_const(index) function pointer
    nullptr,  // get(index) function pointer
    nullptr,  // fetch(index, &value) function pointer
    nullptr,  // assign(index, value) function pointer
    nullptr  // resize(index) function pointer
  },
  {
    "distance_des",  // name
    ::rosidl_typesupport_introspection_cpp::ROS_TYPE_FLOAT,  // type
    0,  // upper bound of string
    nullptr,  // members of sub message
    false,  // is array
    0,  // array size
    false,  // is upper bound
    offsetof(drone_c::msg::AltitudeLidar, distance_des),  // bytes offset in struct
    nullptr,  // default value
    nullptr,  // size() function pointer
    nullptr,  // get_const(index) function pointer
    nullptr,  // get(index) function pointer
    nullptr,  // fetch(index, &value) function pointer
    nullptr,  // assign(index, value) function pointer
    nullptr  // resize(index) function pointer
  }
};

static const ::rosidl_typesupport_introspection_cpp::MessageMembers AltitudeLidar_message_members = {
  "drone_c::msg",  // message namespace
  "AltitudeLidar",  // message name
  2,  // number of fields
  sizeof(drone_c::msg::AltitudeLidar),
  AltitudeLidar_message_member_array,  // message members
  AltitudeLidar_init_function,  // function to initialize message memory (memory has to be allocated)
  AltitudeLidar_fini_function  // function to terminate message instance (will not free memory)
};

static const rosidl_message_type_support_t AltitudeLidar_message_type_support_handle = {
  ::rosidl_typesupport_introspection_cpp::typesupport_identifier,
  &AltitudeLidar_message_members,
  get_message_typesupport_handle_function,
};

}  // namespace rosidl_typesupport_introspection_cpp

}  // namespace msg

}  // namespace drone_c


namespace rosidl_typesupport_introspection_cpp
{

template<>
ROSIDL_TYPESUPPORT_INTROSPECTION_CPP_PUBLIC
const rosidl_message_type_support_t *
get_message_type_support_handle<drone_c::msg::AltitudeLidar>()
{
  return &::drone_c::msg::rosidl_typesupport_introspection_cpp::AltitudeLidar_message_type_support_handle;
}

}  // namespace rosidl_typesupport_introspection_cpp

#ifdef __cplusplus
extern "C"
{
#endif

ROSIDL_TYPESUPPORT_INTROSPECTION_CPP_PUBLIC
const rosidl_message_type_support_t *
ROSIDL_TYPESUPPORT_INTERFACE__MESSAGE_SYMBOL_NAME(rosidl_typesupport_introspection_cpp, drone_c, msg, AltitudeLidar)() {
  return &::drone_c::msg::rosidl_typesupport_introspection_cpp::AltitudeLidar_message_type_support_handle;
}

#ifdef __cplusplus
}
#endif
