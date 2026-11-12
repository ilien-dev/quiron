## What this PR does

Adds support for creating a dedicated VPC on DigitalOcean when the `--network-cidr` flag is passed to `kops create cluster`. Until now, droplets and load balancers were always placed in the region's default VPC.

## Changes

- Adds a new `VPC` task under `upup/pkg/fi/cloudup/dotasks` that finds or creates a VPC with the requested IP range.
- Adds a VPC model builder in `pkg/model/domodel` that emits the task only when `networkCIDR` is set in the cluster spec.
- Wires the VPC into the droplet and load balancer tasks so they are created inside the new network.
- Extends the DO cloud interface with a VPC service client.
- Deletes the VPC during `kops delete cluster`, after the resources that depend on it.

## Behavior

If `--network-cidr` is omitted, nothing changes and the default VPC is used, so existing clusters are unaffected.

## Testing

Created and deleted clusters with and without the flag, and verified the VPC, droplets and load balancer in the DO console.
