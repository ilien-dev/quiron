# What Is the Cloud?

“The cloud” is one of those technology terms that sounds mysterious until you realize how ordinary it is.

When you save a photo to Google Drive, stream a movie from Netflix, deploy an application to AWS, or open an email in your browser, you are using the cloud. Your data or software is running on computers somewhere else, and you access it through a network—usually the internet.

That is the simplest definition:

> Cloud computing is the delivery of computing resources over a network, on demand.

Those resources can include storage, databases, servers, networking, analytics, and complete applications.

## The Cloud Is Still Someone Else’s Computer

The cloud is not floating in the sky. It consists of physical machines housed in data centers around the world.

A data center may contain thousands of servers, along with networking equipment, backup power, cooling systems, fire suppression, and strict physical security. Companies such as Amazon, Microsoft, and Google operate enormous networks of these facilities.

What makes the cloud different from simply renting a computer is the layer of automation built around it. Cloud platforms let you create, resize, and delete resources in minutes—often through an API—without physically touching any hardware.

Need a server? You can create one.

Need more storage? Increase it with a few clicks.

Traffic suddenly dropped? Remove unnecessary resources and stop paying for them.

This flexibility is one of the cloud’s defining features.

## Before Cloud Computing

Traditionally, a company that needed computing infrastructure had to buy it.

Imagine launching an online store before cloud platforms existed. You might have needed to:

1. Estimate how much traffic the store would receive.
2. Purchase enough servers to handle that traffic.
3. Find somewhere to host them.
4. Install operating systems and applications.
5. Configure networking, backups, and security.
6. Replace failed or outdated hardware.

This required a large upfront investment, and planning was difficult. Buy too little capacity and the site might crash. Buy too much and expensive equipment would sit unused.

Cloud computing changes this model. Instead of purchasing hardware, businesses rent resources as needed. This shifts infrastructure from a large upfront cost to an ongoing, usage-based expense.

## The Main Cloud Service Models

Cloud services are often divided into three broad categories.

### Infrastructure as a Service

Infrastructure as a Service, or **IaaS**, provides basic computing building blocks such as virtual machines, storage, and networks.

You manage the operating system and the software installed on it, while the provider manages the physical hardware. Amazon EC2, Azure Virtual Machines, and Google Compute Engine are common examples.

IaaS offers flexibility, but it also leaves you responsible for more maintenance.

### Platform as a Service

Platform as a Service, or **PaaS**, gives developers an environment for running applications without managing as much infrastructure.

You deploy your code, and the platform handles tasks such as configuring servers, balancing traffic, and restarting failed processes. Heroku and Google App Engine are familiar examples.

PaaS can make deployment much simpler, although it may give you less control over the underlying environment.

### Software as a Service

Software as a Service, or **SaaS**, delivers a complete application over the internet.

Users simply open the application, usually in a browser, while the provider operates everything behind it. GitHub, Slack, Dropbox, and Gmail are examples of SaaS products.

Most people use SaaS every day, even if they never think of it as cloud computing.

## Public, Private, and Hybrid Clouds

Not every cloud environment works the same way.

A **public cloud** uses infrastructure operated by a third-party provider and shared among many customers. Each customer’s resources are logically isolated, even though some physical hardware may be shared.

A **private cloud** is dedicated to one organization. It may run in the organization’s own data center or be hosted by another company. Private clouds can provide greater control but usually require more work and expense.

A **hybrid cloud** combines private infrastructure with public cloud services. For example, a company might keep sensitive records on private systems while using a public cloud to handle website traffic.

Organizations may also adopt a **multi-cloud** strategy, using services from more than one public cloud provider.

## Why Developers Use the Cloud

For developers, the cloud makes experimentation and distribution dramatically easier.

A small team can launch an application worldwide without building a data center. Infrastructure can be described in code, created automatically, and reproduced across environments. Managed databases reduce administrative work. Serverless platforms can run functions without requiring developers to manage servers directly.

Cloud platforms also make scaling more practical. An application can add resources during periods of heavy demand and remove them later.

However, the cloud is not automatically cheap, simple, or secure. Poorly configured services can expose data. Unmonitored resources can generate surprising bills. Applications built too closely around one provider’s services may be difficult to move elsewhere.

The provider secures the underlying platform, but customers are still responsible for how they configure and use it. This is commonly called the **shared responsibility model**.

## A Useful Mental Model

Think of cloud computing like electricity.

Most businesses do not build their own power stations. They connect to a grid, consume what they need, and pay based on usage. The provider operates the complex infrastructure behind the service.

Cloud computing applies a similar idea to technology resources. Instead of owning every server, organizations request computing capacity when they need it.

The abstraction is not perfect—you still need to understand architecture, cost, reliability, and security—but it captures the essential shift.

The cloud is not a place or a single technology. It is a way of providing computing resources: remotely, automatically, elastically, and on demand.