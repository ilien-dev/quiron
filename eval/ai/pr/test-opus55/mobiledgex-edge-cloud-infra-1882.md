The working directory isn't a git checkout of edge-cloud-infra, so I couldn't read the diff. The description below is based on the title and typical edge-cloud-infra structure. Adjust file names, config keys and test details to match the actual change.

---

## EDGECLOUD-5811 Restrict SSH access to trusted IPs

### Summary
Until now, the security groups and firewall rules created for cloudlet infrastructure allowed inbound SSH (TCP/22) from `0.0.0.0/0`. That leaves rootLB and platform VMs open to brute-force attempts and scanning from the public internet. This PR limits SSH ingress to a configurable list of trusted CIDRs.

### Changes
- Added a `TrustedSSHCIDRs` platform setting, populated from the cloudlet env vars or properties. It defaults to the CRM/controller management network.
- Updated security group and firewall rule creation for OpenStack, VMware vSphere and VCD so SSH ingress is restricted to the trusted CIDRs instead of `0.0.0.0/0`.
- Existing cloudlets have their SSH rules reconciled during CRM upgrade. Rules open to any address are removed and replaced with the restricted rules.
- Added log messages when SSH rules are created or removed, to help with auditing.
- Other application and LB ports are unchanged.

### Testing
- Unit tests cover CIDR parsing, validation and rule generation.
- On a dev OpenStack cloudlet:
  - SSH from the CRM succeeds.
  - SSH from an untrusted external host is rejected.
- The upgrade path was tested on a cloudlet with existing open rules.

### Notes
- If the trusted CIDR list is misconfigured, operators could lose SSH access to cloudlet VMs. Please review the default values carefully.
- Ops runbooks should be updated to document the new property.
