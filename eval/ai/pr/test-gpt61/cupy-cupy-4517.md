This PR overhauls `cupy.core.dlpack` to use the bundled upstream `dlpack.h` header and fixes several issues in tensor exchange, capsule validation, and memory cleanup. Using the upstream definitions reduces duplication and makes future DLPack updates easier to maintain.

The changes include:

- Import DLPack declarations from the bundled header and add the upstream enum values `kDLVulkan` and `kDLBfloat`.
- Export ROCm tensors with `kDLROCM` when CuPy is built against HIP, distinguishing them from CUDA tensors using `kDLGPU`.
- Validate capsules with `PyCapsule_IsValid()` and reject attempts to consume an already-used DLPack capsule.
- Fix the segmentation fault caused by consuming a capsule twice, including guarding cleanup against a null tensor pointer.
- Correct an invalid memory access during tensor cleanup and defer marking a capsule as consumed until conversion succeeds.
- Update build dependencies so changes to the DLPack header trigger recompilation of the relevant extension.
- Add regression tests for capsule handling and repeated consumption.

The documentation also clarifies that callers must coordinate CUDA/HIP streams when exchanging tensors, because the current DLPack specification does not provide synchronization guarantees. These changes make failures explicit and improve the reliability of zero-copy interoperability across supported GPU backends.

Closes [#3611](https://github.com/cupy/cupy/issues/3611) and [#4513](https://github.com/cupy/cupy/issues/4513). Implementation details: [#4517](https://github.com/cupy/cupy/pull/4517).
