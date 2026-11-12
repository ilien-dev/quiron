add_*_script: fix incorrect typed_pos_args allowing built targets

The script registration methods accept different argument types depending
on when their scripts run. Installation scripts can use build outputs,
but post-configuration and distribution scripts cannot assume that those
outputs exist. Their typed_pos_args declarations must reflect that
distinction instead of accepting the same target types everywhere.

Restrict meson.add_postconf_script() and meson.add_dist_script() to
strings, File objects, and ExternalProgram objects, both for the script
and for additional positional arguments. This rejects build targets,
custom targets, and custom target indexes during argument validation,
before they reach code that cannot handle them in these contexts.

Keep support for built executables as the script passed to
meson.add_install_script(), and retain support for build targets,
custom targets, and custom target indexes in its additional arguments.
Installation happens after the build, so these uses remain valid.

Update the corresponding Python type annotations to match the accepted
arguments. The decorators and method signatures should describe the
same interface, making the restrictions clear to both callers and
static analysis.

This brings validation into line with the documented behavior of the
three methods and gives invalid calls an argument type error at the
point of use. Valid installation scripts continue to receive paths
to their target outputs as before.

[Meson script API reference](https://mesonbuild.com/Reference-manual_builtin_meson.html)
