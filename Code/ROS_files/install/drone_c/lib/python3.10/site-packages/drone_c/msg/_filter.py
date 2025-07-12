# generated from rosidl_generator_py/resource/_idl.py.em
# with input from drone_c:msg/Filter.idl
# generated code does not contain a copyright notice


# Import statements for member types

import builtins  # noqa: E402, I100

import math  # noqa: E402, I100

import rosidl_parser.definition  # noqa: E402, I100


class Metaclass_Filter(type):
    """Metaclass of message 'Filter'."""

    _CREATE_ROS_MESSAGE = None
    _CONVERT_FROM_PY = None
    _CONVERT_TO_PY = None
    _DESTROY_ROS_MESSAGE = None
    _TYPE_SUPPORT = None

    __constants = {
    }

    @classmethod
    def __import_type_support__(cls):
        try:
            from rosidl_generator_py import import_type_support
            module = import_type_support('drone_c')
        except ImportError:
            import logging
            import traceback
            logger = logging.getLogger(
                'drone_c.msg.Filter')
            logger.debug(
                'Failed to import needed modules for type support:\n' +
                traceback.format_exc())
        else:
            cls._CREATE_ROS_MESSAGE = module.create_ros_message_msg__msg__filter
            cls._CONVERT_FROM_PY = module.convert_from_py_msg__msg__filter
            cls._CONVERT_TO_PY = module.convert_to_py_msg__msg__filter
            cls._TYPE_SUPPORT = module.type_support_msg__msg__filter
            cls._DESTROY_ROS_MESSAGE = module.destroy_ros_message_msg__msg__filter

    @classmethod
    def __prepare__(cls, name, bases, **kwargs):
        # list constant names here so that they appear in the help text of
        # the message class under "Data and other attributes defined here:"
        # as well as populate each message instance
        return {
        }


class Filter(metaclass=Metaclass_Filter):
    """Message class 'Filter'."""

    __slots__ = [
        '_std_beta',
        '_high_beta',
        '_low_beta',
    ]

    _fields_and_field_types = {
        'std_beta': 'float',
        'high_beta': 'float',
        'low_beta': 'float',
    }

    SLOT_TYPES = (
        rosidl_parser.definition.BasicType('float'),  # noqa: E501
        rosidl_parser.definition.BasicType('float'),  # noqa: E501
        rosidl_parser.definition.BasicType('float'),  # noqa: E501
    )

    def __init__(self, **kwargs):
        assert all('_' + key in self.__slots__ for key in kwargs.keys()), \
            'Invalid arguments passed to constructor: %s' % \
            ', '.join(sorted(k for k in kwargs.keys() if '_' + k not in self.__slots__))
        self.std_beta = kwargs.get('std_beta', float())
        self.high_beta = kwargs.get('high_beta', float())
        self.low_beta = kwargs.get('low_beta', float())

    def __repr__(self):
        typename = self.__class__.__module__.split('.')
        typename.pop()
        typename.append(self.__class__.__name__)
        args = []
        for s, t in zip(self.__slots__, self.SLOT_TYPES):
            field = getattr(self, s)
            fieldstr = repr(field)
            # We use Python array type for fields that can be directly stored
            # in them, and "normal" sequences for everything else.  If it is
            # a type that we store in an array, strip off the 'array' portion.
            if (
                isinstance(t, rosidl_parser.definition.AbstractSequence) and
                isinstance(t.value_type, rosidl_parser.definition.BasicType) and
                t.value_type.typename in ['float', 'double', 'int8', 'uint8', 'int16', 'uint16', 'int32', 'uint32', 'int64', 'uint64']
            ):
                if len(field) == 0:
                    fieldstr = '[]'
                else:
                    assert fieldstr.startswith('array(')
                    prefix = "array('X', "
                    suffix = ')'
                    fieldstr = fieldstr[len(prefix):-len(suffix)]
            args.append(s[1:] + '=' + fieldstr)
        return '%s(%s)' % ('.'.join(typename), ', '.join(args))

    def __eq__(self, other):
        if not isinstance(other, self.__class__):
            return False
        if self.std_beta != other.std_beta:
            return False
        if self.high_beta != other.high_beta:
            return False
        if self.low_beta != other.low_beta:
            return False
        return True

    @classmethod
    def get_fields_and_field_types(cls):
        from copy import copy
        return copy(cls._fields_and_field_types)

    @builtins.property
    def std_beta(self):
        """Message field 'std_beta'."""
        return self._std_beta

    @std_beta.setter
    def std_beta(self, value):
        if __debug__:
            assert \
                isinstance(value, float), \
                "The 'std_beta' field must be of type 'float'"
            assert not (value < -3.402823466e+38 or value > 3.402823466e+38) or math.isinf(value), \
                "The 'std_beta' field must be a float in [-3.402823466e+38, 3.402823466e+38]"
        self._std_beta = value

    @builtins.property
    def high_beta(self):
        """Message field 'high_beta'."""
        return self._high_beta

    @high_beta.setter
    def high_beta(self, value):
        if __debug__:
            assert \
                isinstance(value, float), \
                "The 'high_beta' field must be of type 'float'"
            assert not (value < -3.402823466e+38 or value > 3.402823466e+38) or math.isinf(value), \
                "The 'high_beta' field must be a float in [-3.402823466e+38, 3.402823466e+38]"
        self._high_beta = value

    @builtins.property
    def low_beta(self):
        """Message field 'low_beta'."""
        return self._low_beta

    @low_beta.setter
    def low_beta(self, value):
        if __debug__:
            assert \
                isinstance(value, float), \
                "The 'low_beta' field must be of type 'float'"
            assert not (value < -3.402823466e+38 or value > 3.402823466e+38) or math.isinf(value), \
                "The 'low_beta' field must be a float in [-3.402823466e+38, 3.402823466e+38]"
        self._low_beta = value
