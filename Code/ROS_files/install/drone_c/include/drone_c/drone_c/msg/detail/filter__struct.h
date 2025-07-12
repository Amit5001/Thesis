// generated from rosidl_generator_c/resource/idl__struct.h.em
// with input from drone_c:msg/Filter.idl
// generated code does not contain a copyright notice

#ifndef DRONE_C__MSG__DETAIL__FILTER__STRUCT_H_
#define DRONE_C__MSG__DETAIL__FILTER__STRUCT_H_

#ifdef __cplusplus
extern "C"
{
#endif

#include <stdbool.h>
#include <stddef.h>
#include <stdint.h>


// Constants defined in the message

/// Struct defined in msg/Filter in the package drone_c.
typedef struct drone_c__msg__Filter
{
  float std_beta;
  float high_beta;
  float low_beta;
} drone_c__msg__Filter;

// Struct for a sequence of drone_c__msg__Filter.
typedef struct drone_c__msg__Filter__Sequence
{
  drone_c__msg__Filter * data;
  /// The number of valid items in data
  size_t size;
  /// The number of allocated items in data
  size_t capacity;
} drone_c__msg__Filter__Sequence;

#ifdef __cplusplus
}
#endif

#endif  // DRONE_C__MSG__DETAIL__FILTER__STRUCT_H_
