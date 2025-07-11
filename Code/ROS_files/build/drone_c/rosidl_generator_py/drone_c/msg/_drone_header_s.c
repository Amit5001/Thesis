// generated from rosidl_generator_py/resource/_idl_support.c.em
// with input from drone_c:msg/DroneHeader.idl
// generated code does not contain a copyright notice
#define NPY_NO_DEPRECATED_API NPY_1_7_API_VERSION
#include <Python.h>
#include <stdbool.h>
#ifndef _WIN32
# pragma GCC diagnostic push
# pragma GCC diagnostic ignored "-Wunused-function"
#endif
#include "numpy/ndarrayobject.h"
#ifndef _WIN32
# pragma GCC diagnostic pop
#endif
#include "rosidl_runtime_c/visibility_control.h"
#include "drone_c/msg/detail/drone_header__struct.h"
#include "drone_c/msg/detail/drone_header__functions.h"

#include "rosidl_runtime_c/primitives_sequence.h"
#include "rosidl_runtime_c/primitives_sequence_functions.h"


ROSIDL_GENERATOR_C_EXPORT
bool drone_c__msg__drone_header__convert_from_py(PyObject * _pymsg, void * _ros_message)
{
  // check that the passed message is of the expected Python class
  {
    char full_classname_dest[38];
    {
      char * class_name = NULL;
      char * module_name = NULL;
      {
        PyObject * class_attr = PyObject_GetAttrString(_pymsg, "__class__");
        if (class_attr) {
          PyObject * name_attr = PyObject_GetAttrString(class_attr, "__name__");
          if (name_attr) {
            class_name = (char *)PyUnicode_1BYTE_DATA(name_attr);
            Py_DECREF(name_attr);
          }
          PyObject * module_attr = PyObject_GetAttrString(class_attr, "__module__");
          if (module_attr) {
            module_name = (char *)PyUnicode_1BYTE_DATA(module_attr);
            Py_DECREF(module_attr);
          }
          Py_DECREF(class_attr);
        }
      }
      if (!class_name || !module_name) {
        return false;
      }
      snprintf(full_classname_dest, sizeof(full_classname_dest), "%s.%s", module_name, class_name);
    }
    assert(strncmp("drone_c.msg._drone_header.DroneHeader", full_classname_dest, 37) == 0);
  }
  drone_c__msg__DroneHeader * ros_message = _ros_message;
  {  // mac_adress
    PyObject * field = PyObject_GetAttrString(_pymsg, "mac_adress");
    if (!field) {
      return false;
    }
    {
      // TODO(dirk-thomas) use a better way to check the type before casting
      assert(field->ob_type != NULL);
      assert(field->ob_type->tp_name != NULL);
      assert(strcmp(field->ob_type->tp_name, "numpy.ndarray") == 0);
      PyArrayObject * seq_field = (PyArrayObject *)field;
      Py_INCREF(seq_field);
      assert(PyArray_NDIM(seq_field) == 1);
      assert(PyArray_TYPE(seq_field) == NPY_INT32);
      Py_ssize_t size = 6;
      int32_t * dest = ros_message->mac_adress;
      for (Py_ssize_t i = 0; i < size; ++i) {
        int32_t tmp = *(npy_int32 *)PyArray_GETPTR1(seq_field, i);
        memcpy(&dest[i], &tmp, sizeof(int32_t));
      }
      Py_DECREF(seq_field);
    }
    Py_DECREF(field);
  }
  {  // drone_mode
    PyObject * field = PyObject_GetAttrString(_pymsg, "drone_mode");
    if (!field) {
      return false;
    }
    assert(PyLong_Check(field));
    ros_message->drone_mode = (int32_t)PyLong_AsLong(field);
    Py_DECREF(field);
  }
  {  // drone_filter
    PyObject * field = PyObject_GetAttrString(_pymsg, "drone_filter");
    if (!field) {
      return false;
    }
    assert(PyLong_Check(field));
    ros_message->drone_filter = (int32_t)PyLong_AsLong(field);
    Py_DECREF(field);
  }
  {  // is_armed
    PyObject * field = PyObject_GetAttrString(_pymsg, "is_armed");
    if (!field) {
      return false;
    }
    assert(PyBool_Check(field));
    ros_message->is_armed = (Py_True == field);
    Py_DECREF(field);
  }
  {  // voltage
    PyObject * field = PyObject_GetAttrString(_pymsg, "voltage");
    if (!field) {
      return false;
    }
    assert(PyFloat_Check(field));
    ros_message->voltage = (float)PyFloat_AS_DOUBLE(field);
    Py_DECREF(field);
  }
  {  // current
    PyObject * field = PyObject_GetAttrString(_pymsg, "current");
    if (!field) {
      return false;
    }
    assert(PyFloat_Check(field));
    ros_message->current = (float)PyFloat_AS_DOUBLE(field);
    Py_DECREF(field);
  }

  return true;
}

ROSIDL_GENERATOR_C_EXPORT
PyObject * drone_c__msg__drone_header__convert_to_py(void * raw_ros_message)
{
  /* NOTE(esteve): Call constructor of DroneHeader */
  PyObject * _pymessage = NULL;
  {
    PyObject * pymessage_module = PyImport_ImportModule("drone_c.msg._drone_header");
    assert(pymessage_module);
    PyObject * pymessage_class = PyObject_GetAttrString(pymessage_module, "DroneHeader");
    assert(pymessage_class);
    Py_DECREF(pymessage_module);
    _pymessage = PyObject_CallObject(pymessage_class, NULL);
    Py_DECREF(pymessage_class);
    if (!_pymessage) {
      return NULL;
    }
  }
  drone_c__msg__DroneHeader * ros_message = (drone_c__msg__DroneHeader *)raw_ros_message;
  {  // mac_adress
    PyObject * field = NULL;
    field = PyObject_GetAttrString(_pymessage, "mac_adress");
    if (!field) {
      return NULL;
    }
    assert(field->ob_type != NULL);
    assert(field->ob_type->tp_name != NULL);
    assert(strcmp(field->ob_type->tp_name, "numpy.ndarray") == 0);
    PyArrayObject * seq_field = (PyArrayObject *)field;
    assert(PyArray_NDIM(seq_field) == 1);
    assert(PyArray_TYPE(seq_field) == NPY_INT32);
    assert(sizeof(npy_int32) == sizeof(int32_t));
    npy_int32 * dst = (npy_int32 *)PyArray_GETPTR1(seq_field, 0);
    int32_t * src = &(ros_message->mac_adress[0]);
    memcpy(dst, src, 6 * sizeof(int32_t));
    Py_DECREF(field);
  }
  {  // drone_mode
    PyObject * field = NULL;
    field = PyLong_FromLong(ros_message->drone_mode);
    {
      int rc = PyObject_SetAttrString(_pymessage, "drone_mode", field);
      Py_DECREF(field);
      if (rc) {
        return NULL;
      }
    }
  }
  {  // drone_filter
    PyObject * field = NULL;
    field = PyLong_FromLong(ros_message->drone_filter);
    {
      int rc = PyObject_SetAttrString(_pymessage, "drone_filter", field);
      Py_DECREF(field);
      if (rc) {
        return NULL;
      }
    }
  }
  {  // is_armed
    PyObject * field = NULL;
    field = PyBool_FromLong(ros_message->is_armed ? 1 : 0);
    {
      int rc = PyObject_SetAttrString(_pymessage, "is_armed", field);
      Py_DECREF(field);
      if (rc) {
        return NULL;
      }
    }
  }
  {  // voltage
    PyObject * field = NULL;
    field = PyFloat_FromDouble(ros_message->voltage);
    {
      int rc = PyObject_SetAttrString(_pymessage, "voltage", field);
      Py_DECREF(field);
      if (rc) {
        return NULL;
      }
    }
  }
  {  // current
    PyObject * field = NULL;
    field = PyFloat_FromDouble(ros_message->current);
    {
      int rc = PyObject_SetAttrString(_pymessage, "current", field);
      Py_DECREF(field);
      if (rc) {
        return NULL;
      }
    }
  }

  // ownership of _pymessage is transferred to the caller
  return _pymessage;
}
