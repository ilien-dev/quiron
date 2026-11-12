# Load testing with JMeter

Your API works fine on your laptop. It passes every unit test, the integration suite is green, and the staging environment hums along with three QA engineers clicking around. Then launch day arrives, a few thousand real users show up, and response times climb into the tens of seconds.

Load testing exists to find that failure before your users do. In this post I'll walk through how to do it with **Apache JMeter**: the core concepts, a realistic test plan, how to run it properly, and how to read the results without fooling yourself.

## Why JMeter?

There are plenty of load testing tools: k6, Gatling, Locust, Artillery. JMeter is the oldest of the group, and it's still widely used for good reasons:

- **Free and open source**, maintained by the Apache Software Foundation.
- **Protocol breadth.** HTTP(S) is the headline, but it also speaks JDBC, JMS, LDAP, FTP, SMTP, TCP and more.
- **GUI for building tests**, which lowers the barrier for people who don't want to write code.
- **Huge plugin ecosystem** and years of Stack Overflow answers.
- **Distributed testing** built in, so you can generate load from multiple machines.

The downsides are real too. Test plans are XML (`.jmx`) files that diff badly in code review, and the GUI is dated. JMeter is also thread-per-user, so it uses more memory per virtual user than event-driven tools. For most teams testing web APIs at moderate scale, it's still a perfectly good choice.

## Installing

JMeter is a Java application, so you need a JDK first (check the JMeter docs for the minimum supported version for your release).

```bash
java -version
```

Then download the binary archive from the [Apache JMeter site](https://jmeter.apache.org/download_jmeter.cgi), extract it, and run `bin/jmeter` (or `bin/jmeter.bat` on Windows). The GUI opens with an empty test plan.

A rule worth memorizing now: **the GUI is for building and debugging tests, not for running them under load.** We'll come back to that.

## The core building blocks

JMeter test plans are trees of elements. Learn these and you can read any plan:

| Element | Purpose |
|---|---|
| **Thread Group** | Defines the virtual users: how many, how fast they ramp up, and how long they run |
| **Sampler** | Sends a request (HTTP Request, JDBC Request, etc.) |
| **Config Element** | Shared settings, like HTTP Request Defaults or CSV Data Set Config |
| **Timer** | Adds delays between requests to model think time |
| **Assertion** | Checks that the response is actually correct |
| **Pre/Post Processor** | Modifies requests or extracts data from responses |
| **Listener** | Collects and displays results |

Execution order matters: config elements first, then pre-processors, timers, the sampler, post-processors, assertions, and finally listeners. Scope is determined by where an element sits in the tree.

## Building a realistic test plan

Let's test a hypothetical REST API with a login endpoint and a product listing. The scenario: each user logs in, fetches products a few times, and views a single product.

### 1. Thread Group

Right-click **Test Plan → Add → Threads → Thread Group**. The key settings:

- **Number of Threads (users):** 50
- **Ramp-up period (seconds):** 60
- **Loop Count:** or use *Duration* under the scheduler section

Ramp-up is important. If you set 50 threads with a ramp-up of 0, all 50 hit the server in the same instant, which is a spike test, not a load test. A ramp of 60 seconds adds roughly one user every 1.2 seconds, which lets you see how the system behaves as load grows.

Rather than hardcoding these values, parameterize them:

```
Number of Threads: ${__P(users,10)}
Ramp-up:           ${__P(rampup,30)}
Duration:          ${__P(duration,300)}
```

`__P` reads a property passed on the command line, falling back to the default. That makes the same `.jmx` reusable from a smoke test to a full load run.

### 2. HTTP Request Defaults

Add **Config Element → HTTP Request Defaults** and set the server name, port, and protocol once. Individual samplers then only need a path. This also makes it trivial to point the same plan at staging versus a pre-production environment.

Add an **HTTP Header Manager** for `Content-Type: application/json` and `Accept: application/json`.

### 3. Test data with CSV Data Set Config

If every virtual user logs in as the same account, you're testing your cache, not your system. Create `users.csv`:

```csv
username,password
alice,secret1
bob,secret2
carol,secret3
```

Add **Config Element → CSV Data Set Config**, point it at the file, set variable names to `username,password`, and choose how to handle end of file. Now reference them in requests as `${username}` and `${password}`.

### 4. Samplers

Add an **HTTP Request** for login:

- Method: `POST`
- Path: `/api/auth/login`
- Body: `{"username":"${username}","password":"${password}"}`

### 5. Correlation: extracting dynamic values

The login response probably returns a token. Subsequent requests need it. Add a **JSON Extractor** as a child of the login sampler:

- Variable name: `token`
- JSON path: `$.accessToken`
- Default value: `TOKEN_NOT_FOUND`

That default value is a small trick that pays off: if extraction fails, you'll see `TOKEN_NOT_FOUND` in your failing requests instead of a confusing empty string.

Then add an HTTP Header Manager with `Authorization: Bearer ${token}` for the following requests.

Add the next samplers: `GET /api/products` and `GET /api/products/${productId}`. You can extract `productId` from the list response with another JSON Extractor (for example `$.items[0].id`), so the plan follows a real user's path.

### 6. Assertions

A server returning `200 OK` with an error body, or a fast `503` from a load balancer, can make your numbers look wonderful. Always assert on correctness:

- **Response Assertion** on the response code (`200`)
- **JSON Assertion** to check that `$.items` exists

Without assertions, JMeter treats most HTTP responses below 400 as successes and happily reports a fast, broken system.

### 7. Timers

Real users don't fire requests back-to-back. Add a **Uniform Random Timer** (say, constant delay 1000 ms, random deviation 2000 ms) to model think time. Without timers, each thread hammers the server as fast as it can, and 50 threads behave like hundreds of real users. That may be what you want for a stress test, but know that you're choosing it.

## Debugging in the GUI

Before scaling up, run with a single thread and add a **View Results Tree** listener. Inspect each request and response, and confirm the token is extracted, the headers are right, and the assertions pass.

Then **disable or delete the View Results Tree**. Listeners that store every sample consume heavy memory and CPU, and they will distort your results at load.

## Running the test properly: non-GUI mode

Run the real test from the command line:

```bash
jmeter -n -t plan.jmx \
  -Jusers=50 -Jrampup=60 -Jduration=600 \
  -l results.jtl \
  -e -o report/
```

What those flags do:

- `-n` runs without the GUI
- `-t` is the test plan
- `-J` sets a JMeter property (read via `__P`)
- `-l` writes raw results to a `.jtl` file
- `-e -o` generates the HTML dashboard into `report/` (the directory must be empty or nonexistent)

Open `report/index.html` and you get response time percentiles, throughput over time, error breakdowns, and more.

Also worth doing:

- **Run the load generator on a separate machine** from the system under test. Otherwise they compete for CPU.
- **Give JMeter enough heap.** Adjust the `HEAP` setting in the startup script if you run many threads.
- **Watch the generator itself.** If its CPU is pegged near 100%, your numbers reflect the generator's limits, not your app's.

## Reading the results

The dashboard has plenty of charts, but a handful of numbers matter most.

**Percentiles over averages.** An average of 300 ms can hide the fact that 5% of users wait 6 seconds. Look at the 90th, 95th, and 99th percentiles. Averages are fine as a headline but terrible as a verdict.

**Error rate.** Anything above your agreed threshold (often well under 1%) deserves investigation. Look at *which* errors: timeouts, 5xx responses, connection refused, and assertion failures each point to different problems.

**Throughput.** Requests per second the system actually sustained. Plot it against response time: a healthy system shows throughput rising with users until it plateaus. If throughput flattens while latency climbs, you've found a bottleneck. If throughput *drops*, you've probably pushed past saturation.

**The shape over time.** Does response time creep upward across a 30-minute run? That's a classic sign of a memory leak, connection pool exhaustion, or a growing queue. A short test would miss it entirely.

A useful habit is to define success criteria *before* running: for example, "p95 under 500 ms and under 0.5% errors at 200 concurrent users." Otherwise it's tempting to rationalize whatever number comes out.

## Types of tests worth running

- **Smoke test:** 1–5 users, to verify the script works.
- **Load test:** expected production traffic, sustained.
- **Stress test:** ramp beyond expected load to find the breaking point.
- **Spike test:** sudden surges, to see how the system recovers.
- **Soak test:** moderate load for hours, to find leaks and degradation.

You can reuse one parameterized plan for all of these by changing only the properties.

## Putting it in CI

Because non-GUI mode is just a command, it fits into a pipeline. A common pattern is a short load test on every merge to main, with a longer one nightly. The Maven and Gradle JMeter plugins, or just a Docker image calling the CLI, work well. Fail the build by parsing the `.jtl` file or using a performance plugin that checks your thresholds.

One caution: CI runners are noisy, so use them to catch *regressions* (a 40% jump in p95), not to establish absolute capacity numbers.

## Common pitfalls

1. **Testing from your laptop over Wi-Fi.** You'll measure your network.
2. **No think time and unrealistic data.** Results won't reflect production.
3. **Ignoring cold starts and caches.** Do a warm-up, or at least know which state you're measuring.
4. **Leaving heavy listeners enabled.** They skew the results.
5. **Forgetting about dependencies.** If your service calls a third-party API, decide whether to hit the real one or mock it.
6. **Load testing production without telling anyone.** Coordinate with your team. Please.

## Wrapping up

JMeter isn't the shiniest tool, but it's capable and it rewards a bit of discipline. Build the plan in the GUI, parameterize it, add assertions and realistic data, run it headless from a separate machine, and judge it on percentiles and error rates against criteria you set in advance.

Do that, and "it worked on my machine" becomes "it handled 500 concurrent users with a p95 of 380 ms," which is a much better thing to be able to say on launch day.

What's your experience with JMeter, or have you moved to something else? Let me know in the comments.
