[OpenMP][Plugin] Introduce generic resource pool

Several plugins (CUDA, AMDGPU) each maintain their own ad-hoc pools
for reusable device resources such as streams and events. The logic
is nearly identical: a mutex-protected collection of free resources,
grown on demand and returned after use. Duplicating it makes bug
fixes and tuning harder to apply consistently.

This patch adds a generic ResourcePoolTy template to the common
plugin interface. It is parameterized on a resource type through a
small resource-ref interface providing create, destroy, and reset
operations. The pool hands out resources via getResource(), growing
its backing storage when none are free, and takes them back via
returnResource(). All operations are guarded by a single mutex, and
destruction releases every resource still owned by the pool.

Existing plugin-specific pools are not converted here. Doing so is
left to follow-up patches so each backend change can be reviewed and
bisected independently.

No functional change is intended for existing plugins. The pool is
not yet used, so there is no behavioral difference until the first
backend adopts it.
