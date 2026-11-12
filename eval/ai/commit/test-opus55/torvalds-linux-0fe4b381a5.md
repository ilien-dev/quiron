bpf: Allow bpf_local_storage to be used by sleepable programs

Other map types, such as hash maps, are already usable from sleepable
BPF programs. Extend this to task, sk and inode local storage so that
sleepable and non-sleepable programs can share annotations on the same
kernel objects.

Sleepable programs run inside an RCU tasks trace read-side critical
section (rcu_read_lock_trace() via __bpf_prog_enter_sleepable()),
while non-sleepable programs run under classic RCU (rcu_read_lock()
via __bpf_prog_enter()). Because a local storage element may be
accessed concurrently from either context, it must not be freed until
both a tasks trace grace period and a classic RCU grace period have
elapsed.

Achieve this by freeing storage and its elements with
call_rcu_tasks_trace(), and chaining a call_rcu() from the tasks trace
callback when rcu_trace_implies_rcu_gp() does not hold. With per-CPU
callback queueing for RCU tasks trace, the added latency and
contention remain acceptable for update-heavy workloads.

Update the lockdep assertions in the local storage lookup and update
paths to accept either rcu_read_lock_held() or
rcu_read_lock_trace_held(), and replace the bare rcu_dereference()
calls with rcu_dereference_check() using the combined condition.

Finally, permit these map types in the verifier's sleepable program
map compatibility check and add selftests that exercise task and
inode storage from sleepable LSM programs.
