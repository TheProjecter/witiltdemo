WiTilt V3 is a magic box by SparkFun that includes the following features:
  1. 3-axis accelerometer (1.5g-6.0g range)
  1. 2-axis gyroscope (300 degrees/second)
  1. Bluetooth communication with a host over SPP
  1. Built-in lithium battery (about 10 hours of uninterrupted work)

This Demo program is written in python + pyserial + pygame. It allows access to the built-in configuration menu and runs the monitoring of XYZR channels with 30fps (adjustable parameter):
  1. Displays (text) raw data of channels (acceleration on X,Y,Z axis and rotation speed about Z axes) + realtime
  1. Integrates acceleration and rotation speed to velocity, position, and angle while displaying selected channels (text).
  1. Updates the positions of 2 markers withing some dedicated region. The first marker is related to Z coordinate and angle, while the other one is for X,Y coordinates. Either acceleration, velocity or position can affect the displacement of markers.
  1. Has built-in DSP unit (averaging window implemented so far) which process each data sample and allows employing advanced filtering techniques, such as removing static acceleration caused by gravity component.
  1. Has built-in calibration feature which collects certain number of samples while the module not in use (you need to activate calibration beforehand the monitoring process) and then uses calibration data to fight against ADC drift and change in gravity range (there are 4 hardware ranges: 1.5g, 2g, 3g, 6g which require different calibration data -- subject of loading from a file).