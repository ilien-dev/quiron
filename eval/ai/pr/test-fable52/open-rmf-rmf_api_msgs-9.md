## Summary

Adds a Python module to `rmf_api_msgs` so that Python packages can load the JSON schemas directly, instead of locating the installed schema files by hand or keeping their own copies.

## Motivation

The schemas are currently only convenient to consume from C++, through the generated headers. Python consumers (task dispatchers, fleet adapters written in Python, the API server, test tooling) have to resolve the package share directory and parse the files themselves. This leads to duplicated boilerplate and makes it easy to drift from the schema version that is actually installed.

## Changes

- New `rmf_api_msgs` Python module, installed alongside the existing CMake package.
- The module exposes the schemas shipped in `rmf_api_msgs/schemas` as Python dictionaries, loaded from the installed share directory so there is a single source of truth.
- Build and package manifest updates to install the Python module (`ament_cmake_python`).
- No changes to the schemas themselves or to the existing C++ targets.

## Usage

```python
from rmf_api_msgs import schemas

task_request = schemas.task_request()
```

The returned dictionaries can be passed straight to `jsonschema` for validation.

## Testing

- Built with `colcon build --packages-select rmf_api_msgs`.
- Confirmed that the module imports from an overlay workspace and that every schema loads as valid JSON.

## Notes

This is purely additive, so existing downstream users should be unaffected. Feedback on the module layout and naming is welcome.
