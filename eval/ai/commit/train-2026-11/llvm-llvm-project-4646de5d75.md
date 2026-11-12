[NewPM][CodeGen] Introduce CodeGenPassBuilder to help build codegen pipeline

Following the design of PassBuilder for the IR optimization pipeline,
this patch adds CodeGenPassBuilder, a CRTP-based helper that lets
targets assemble their codegen pipeline under the new pass manager.

The legacy TargetPassConfig mixes pipeline construction, option
handling and pass insertion hooks into a single class tied to the
legacy pass manager. CodeGenPassBuilder separates these concerns:
targets derive from it, override hooks such as addInstSelector() or
addPreEmitPass(), and the base class drives the overall ordering of
IR and machine function passes.

Supporting pieces included here:
  * MachinePassRegistry.def, listing IR and machine passes used by
    codegen so they can be parsed and registered by name.
  * Dummy placeholder passes for machine passes not yet ported, so the
    default pipeline can be expressed in full today.
  * CGPassBuilderOption, collecting the codegen command-line options
    that influence pipeline shape.

No target uses the new builder yet; follow-up patches will port
individual targets and llc.
