build: Disable Visual Studio warning "conditional expression is constant"

Visual Studio emits warning C4127, "conditional expression is constant",
whenever a condition can be evaluated at compile time. curl hits this
constantly and on purpose: `do { ... } while(0)` wrappers in macros,
`while(1)` loops, and checks on `sizeof` or on build-time configuration
values that the compiler can fold away.

The warning does not point at real bugs here. The constant conditions are
deliberate, and in many cases they are the only portable way to write a
macro that behaves like a single statement. Some compiler and
configuration combinations make a condition constant while others do not,
so the same source line may or may not warn depending on the build.

Working around each occurrence would mean adding pragmas or contorting
otherwise clear code just to satisfy one compiler. That adds clutter and
risks diverging from what other compilers expect. The noise also buries
the warnings that matter, especially in builds that use a high warning
level or treat warnings as errors.

Disable the warning for Visual Studio builds instead. Other compilers and
warning classes are unaffected, so the useful diagnostics remain enabled.
