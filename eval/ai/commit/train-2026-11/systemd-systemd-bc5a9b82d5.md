firewall-util-nft: attempt table recreation when add operation fails

Previously, if our table was removed behind our back, for instance by `nft flush ruleset` or by a firewall manager reloading its configuration, any later attempt to add a rule would fail with ENOENT. The caller would then never recover until the service was restarted.

Handle this by retrying once. When the kernel rejects a batch containing an add operation, recreate the table and its chains, then resubmit the original request. If the second attempt fails as well, return that error to the caller, so we never loop forever.

Delete operations are left alone, since a missing table there just means there is nothing to remove.

This makes the masquerade and port forwarding setup used by systemd-networkd and systemd-nspawn resilient against external ruleset changes. No behavior change is expected when the table is intact, as the fallback path is only taken after a failure.
