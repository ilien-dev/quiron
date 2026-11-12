# What is the Cloud?

“The cloud” sounds mysterious, as if our photos, applications, and databases float somewhere above us. In reality, the cloud is physical infrastructure: computers, storage devices, and networking equipment running inside data centers.

What makes it different is how we access and manage those resources. Instead of buying every server yourself, you use computing resources over a network, usually the internet, and pay according to a provider’s pricing model.

For developers, this changes how we build, deploy, and scale software. Let’s break it down.

## From owning computers to renting capabilities

Imagine you’re launching a web application without a cloud provider.

You might purchase a server, find somewhere to run it, configure networking, install an operating system, and set up your application. You also need to handle hardware failures, security updates, backups, and whatever happens when traffic suddenly increases.

With cloud computing, you can provision a virtual server through a dashboard, command-line tool, or API. The provider operates the underlying infrastructure, while you manage the parts relevant to your application.

The difference resembles owning a generator versus buying electricity from a utility. You still need to understand your consumption, but you don’t need to operate the entire power plant.

## What actually happens when you use it?

Suppose you deploy a small application to a cloud platform.

Your application’s code runs on machines in a data center. A network routes incoming requests to those machines. Your database stores information on persistent storage, and monitoring tools collect logs and performance measurements.

When someone visits your application, their browser sends a request across the network. Your application processes it and returns a response.

Nothing supernatural happens. The cloud packages familiar computing components into services you can request and control programmatically.

Virtualization helps make this possible. A physical machine can host multiple isolated virtual machines. Providers also use containers and other isolation mechanisms, depending on the service.

## The three common service models

Cloud services are often grouped into three categories. The main distinction is how much you manage yourself.

### Infrastructure as a Service: IaaS

IaaS gives you foundational resources such as virtual machines, networks, and storage.

You choose the operating system, install dependencies, deploy your application, and maintain much of the software stack. The provider handles the physical hardware.

Think of it as renting a kitchen: the space and equipment are available, but you’re responsible for cooking.

### Platform as a Service: PaaS

PaaS gives you an environment for running applications without managing the underlying servers directly.

You provide your code and configuration. The platform handles more of the runtime, deployment machinery, and infrastructure maintenance.

This can simplify development, although you work within the platform’s supported tools and constraints.

### Software as a Service: SaaS

SaaS is a complete application delivered over a network.

Web-based email, project management tools, and browser-based document editors are familiar examples. You use the software rather than deploying and maintaining its infrastructure.

These categories are useful starting points, but real services sometimes overlap.

## Where does serverless fit?

Serverless computing lets you run code or use backend capabilities without provisioning servers yourself.

For example, a function might execute whenever someone uploads an image. It creates a thumbnail, saves the result, and finishes.

Servers still exist. “Serverless” describes the developer’s operational experience, not the absence of hardware.

Depending on the service, pricing may reflect requests, execution time, or allocated capacity. You still need to consider limits, latency, permissions, and failure handling.

## Why developers use the cloud

One major benefit is speed. Teams can create development environments or deploy applications without waiting for hardware purchases.

Another is elasticity: resources can increase or decrease with demand. An application might need more capacity during a product launch and less afterward. Scaling still requires suitable architecture and configuration; it isn’t automatic for every workload.

Cloud platforms also offer managed databases, messaging systems, object storage, and other building blocks. Using these services can reduce operational work and let teams focus on application behavior.

## The tradeoffs still matter

The cloud doesn’t remove responsibility. It redistributes it.

You must understand which security tasks belong to the provider and which belong to you. Application vulnerabilities, overly broad permissions, and exposed credentials remain your concern.

Costs also require attention. Idle resources, oversized databases, and data transfers can create unexpected bills.

Reliability requires deliberate design, too. A cloud service can fail, and deploying an application doesn’t automatically give it backups or disaster recovery.

Finally, provider-specific services can make migration harder. That tradeoff may be worthwhile, but it should be intentional.

## A practical mental model

Think of the cloud as computing resources delivered as services.

Start with what your application needs: somewhere to run code, somewhere to store data, and a way for components to communicate. Then decide how much operational responsibility you want to keep.

You don’t need every cloud service to build something useful. Understanding a few core components is enough to begin—and to make informed decisions as your application grows.
