// generated from rosidl_generator_c/resource/idl__struct.h.em
// with input from drone_c:msg/AltitudeLidar.idl
// generated code does not contain a copyright notice

#ifndef DRONE_C__MSG__DETAIL__ALTITUDE_LIDAR__STRUCT_H_
#define DRONE_C__MSG__DETAIL__ALTITUDE_LIDAR__STRUCT_H_

#ifdef __cplusplus
extern "C"
{
#endif

#include <stdbool.h>
#include <stddef.h>
#include <stdint.h>


// Constants defined in the message

/// Struct defined in msg/AltitudeLidar in the package drone_c.
typedef struct drone_c__msg__AltitudeLidar
{
  float distance;
} drone_c__msg__AltitudeLidar;

// Struct for a sequence of drone_c__msg__AltitudeLidar.
typedef struct drone_c__msg__AltitudeLidar__Sequence
{
  drone_c__msg__AltitudeLidar * data;
  /// The number of valid items in data
  size_t size;
  /// The number of allocated items in data
  size_t capacity;
} drone_c__msg__AltitudeLidar__Sequence;

#ifdef __cplusplus
}
#endif

#endif  // DRONE_C__MSG__DETAIL__ALTITUDE_LIDAR__STRUCT_H_
