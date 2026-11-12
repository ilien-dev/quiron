This PR adds LEGO BOOST MoveHub support to SharpBrick.PoweredUp, including access to its internal motors and built-in tilt sensor. It extends the SDK’s device model so applications can work with these components through the same programming approach used for other supported hubs.

The change brings the MoveHub’s core movement and sensing capabilities into the library. Applications can control the internal motors and receive tilt sensor data, making it possible to build models that combine motorized actions with responses to changes in the hub’s orientation.

The scope covers:

- MoveHub integration with the existing hub and device abstractions.
- Internal motor support for controlling the hub’s built-in movement hardware.
- Tilt sensor support for accessing orientation-related input.
- Consistent access to these components within the SDK’s established programming model.

Together, these additions make MoveHub a more useful target for applications built on SharpBrick.PoweredUp and provide a foundation for LEGO BOOST projects that need both movement and sensor feedback. They also give developers a clearer starting point for experimenting with the hub’s integrated hardware.

Review should focus on hub discovery, correct mapping of internal devices, motor command behavior, and tilt sensor value handling. Hardware validation should confirm that both internal motors respond correctly and sensor updates reflect changes in orientation.

Repository context: [SharpBrick.PoweredUp](https://github.com/sharpbrick/powered-up).
