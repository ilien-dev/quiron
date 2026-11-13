# A Guide To Designing Low-Cost Ventilators for COVID-19

**[VIDEO SCRIPT: approx. 17 minutes]**

---

## COLD OPEN

**[VISUAL: Archival news footage, March 2020. Hospital corridors. Headlines about ventilator shortages.]**

**NARRATOR (V.O.):**
In March of 2020, hospitals in northern Italy ran out of ventilators. Doctors were forced to decide who got a machine and who didn't. Within weeks, the same fear spread to New York, Madrid, São Paulo, and Mumbai.

And then something remarkable happened. Engineers, students, race car teams, vacuum cleaner companies, and hobbyists in garages all asked the same question: how hard can it be to build a ventilator?

**[VISUAL: Montage of prototypes: plywood frames, windshield wiper motors, 3D-printed parts.]**

**NARRATOR (V.O.):**
The answer turned out to be: much harder than it looks. Pushing air into a lung is easy. Pushing air into a damaged lung, for two weeks straight, without ever hurting the patient, is one of the hardest problems in medical engineering.

Today, we're going to walk through how you design a low-cost ventilator: the physiology, the architecture, the sensors, the safety systems, and the lessons hundreds of teams learned the hard way.

**[TITLE CARD: A Guide To Designing Low-Cost Ventilators for COVID-19]**

---

## SECTION 1: A NECESSARY DISCLAIMER

**[VISUAL: Host on camera, workbench behind them.]**

**HOST:**
Before we start, one thing needs to be absolutely clear. This video is an engineering education piece. It is not a build guide, and nothing here is medical advice.

A ventilator is a life-support device. If it fails, or if it works but delivers the wrong thing, a person can die in minutes. Every design we discuss today required clinicians, regulatory review, and thousands of hours of testing before it went anywhere near a patient. Many never got there at all.

So treat this as a tour of a fascinating design problem. If you want to contribute to this field, the path runs through clinical partners and regulators, not around them.

With that said, let's get into it.

---

## SECTION 2: WHAT A VENTILATOR ACTUALLY DOES

**[VISUAL: Animation of lungs, airways branching down to alveoli.]**

**NARRATOR (V.O.):**
Your lungs contain about 480 million tiny air sacs called alveoli. Oxygen crosses into your blood there, and carbon dioxide crosses out. Normally, your diaphragm pulls down, creates negative pressure, and air flows in.

A mechanical ventilator does the opposite. It uses positive pressure and pushes air in. That is already unnatural, and it's the root of most of the dangers we'll talk about.

**[VISUAL: Animation of alveoli filling with fluid, some collapsing.]**

**NARRATOR (V.O.):**
Severe COVID-19 often caused acute respiratory distress syndrome, or ARDS. In ARDS, the alveoli become inflamed, fill with fluid, and collapse. The lung becomes stiff. Engineers would say its compliance drops. A healthy lung might accept 100 milliliters of air for every centimeter of water pressure. A lung with ARDS might accept 20 or 30.

And the damage isn't uniform. Some regions are collapsed and others are still working. Clinicians call this "baby lung," because the functional part of an adult's lung may be the size of a small child's.

**[VISUAL: Host on camera.]**

**HOST:**
This is why the "just squeeze a bag" idea is so dangerous. Push too much volume into a baby lung and you overstretch the healthy parts. That's volutrauma. Use too much pressure and you get barotrauma. Let the alveoli collapse and snap open with every breath and you get atelectrauma.

A bad ventilator doesn't just fail to help. It actively destroys the lung tissue the patient has left. So the design goal is not moving air. The design goal is precise, gentle, controlled, monitored air.

---

## SECTION 3: THE REQUIREMENTS

**[VISUAL: Spec sheet building on screen, line by line.]**

**NARRATOR (V.O.):**
So what does the machine need to do? During the pandemic, regulators like the UK's MHRA published minimum specifications for rapidly manufactured ventilators, and the numbers were similar everywhere.

**Tidal volume.** This is the amount of air per breath. Lung-protective ventilation targets around 6 milliliters per kilogram of predicted body weight, which is based on height, not actual weight. In practice, you need an adjustable range of roughly 250 to 600 milliliters, with good accuracy.

**Respiratory rate.** Somewhere between 10 and 30 breaths per minute.

**I-to-E ratio.** This is the ratio of inhalation time to exhalation time. One to two is typical, and it should be adjustable. Exhalation is passive, and the patient needs enough time to empty the lungs fully.

**Peak pressure limits.** Plateau pressure should generally stay below 30 centimeters of water, with a hard mechanical limit that can't be exceeded, often around 40.

**PEEP.** This is positive end-expiratory pressure, and it's the one amateurs most often forgot. At the end of exhalation, the ventilator must hold a small pressure in the lungs, typically 5 to 20 centimeters of water. That pressure keeps damaged alveoli from collapsing. For ARDS patients, PEEP is not optional.

**FiO2.** This is the fraction of inspired oxygen, adjustable from room air at 21 percent up to nearly 100 percent.

**[VISUAL: Host on camera.]**

**HOST:**
Then come the requirements that don't fit neatly in a table. The machine has to run continuously for fourteen days or more. That's over half a million breath cycles with no failures. It has to alarm when something goes wrong. It has to survive a power cut. And ideally it has to detect when the patient tries to breathe on their own and help them, instead of fighting them.

That last one is a big deal, and we'll come back to it.

---

## SECTION 4: THREE ARCHITECTURES

**[VISUAL: Three-panel diagram showing the three approaches.]**

**NARRATOR (V.O.):**
Low-cost designs from the pandemic fell into three broad families.

### Architecture One: The Automated Bag Squeezer

**[VISUAL: Animation of a bag-valve-mask being compressed by mechanical arms.]**

**NARRATOR (V.O.):**
Every hospital has manual resuscitators, usually called bag-valve-masks or Ambu bags. They're cheap, already certified, and available by the million. The idea is simple: replace the human hand with a motor.

The best-known example was the MIT Emergency Ventilator project, which used two curved paddles driven by a geared motor. Other teams used cams, linear actuators, or rack-and-pinion mechanisms.

The advantages are real. The air path is an existing medical device, the mechanism is easy to understand, and the parts cost is low.

But the limitations are serious. Bags aren't built for a million cycles and can fatigue. Delivered volume depends on where and how you squeeze, so it has to be calibrated or measured. And the motor works hard: it needs high torque, constant reversing, and continuous duty. Many early prototypes used hobby servos or windshield wiper motors that would never have survived two weeks.

### Architecture Two: The Pneumatic Design

**[VISUAL: Schematic of hospital wall gas, regulator, proportional valve, patient circuit.]**

**NARRATOR (V.O.):**
Hospitals have high-pressure oxygen and medical air piped into the walls. A pneumatic ventilator uses that pressure as its energy source. Valves open to let gas flow to the patient and close to stop it. A separate exhalation valve opens to let the breath out.

This approach has few moving parts and precise control, and it's how many commercial ICU ventilators work. The downsides are that it depends completely on the hospital gas supply, and medical-grade proportional valves became some of the scarcest components on Earth in 2020.

### Architecture Three: The Blower

**[VISUAL: Cutaway of a centrifugal turbine blower.]**

**NARRATOR (V.O.):**
The third approach uses a high-speed turbine, the same technology found in CPAP and BiPAP machines for sleep apnea. The blower pressurizes room air, and its speed is modulated to shape each breath.

Blower designs don't need compressed air and respond quickly, which makes them good for pressure-controlled modes. Several successful emergency designs, including NASA JPL's VITAL and a number of adapted sleep apnea devices, fell broadly into the pneumatic or blower families.

**[VISUAL: Host on camera.]**

**HOST:**
So which is best? It depends on your constraints. And the key lesson of 2020 was that the main constraint wasn't cost. It was supply chain.

A design is only "low-cost" if you can actually get the parts, at volume, during a global shortage, without competing with the established ventilator manufacturers for the same components. The smartest teams designed around parts from other industries, such as automotive, industrial automation, and consumer appliances, so they weren't making the shortage worse.

---

## SECTION 5: SENSORS AND CONTROL

**[VISUAL: Block diagram of sensors, microcontroller, actuator, patient, feedback loop.]**

**NARRATOR (V.O.):**
Whatever the architecture, a ventilator is a closed-loop control system. And you cannot control what you cannot measure.

**Pressure sensing** is the foundation. A sensor in the airway measures pressure in centimeters of water. From it you get peak pressure, plateau pressure, and PEEP, and it's your first line of defense against over-pressurization.

**Flow sensing** is harder. The common low-cost approach is a differential pressure sensor across a known restriction, such as a venturi or an orifice. The pressure drop tells you the flow rate. Integrate flow over time and you get volume.

**[VISUAL: Graph of flow integrating into volume, with drift accumulating.]**

**NARRATOR (V.O.):**
But integration accumulates error. A small sensor offset becomes a large volume error within a few breaths, so designs need to re-zero regularly. Flow readings also change with gas composition, humidity, and temperature. Oxygen-enriched air at body humidity behaves differently from dry room air.

**Oxygen sensing** uses a galvanic cell or other sensor to confirm the delivered FiO2.

### Ventilation Modes

**[VISUAL: Pressure and flow waveforms for each mode.]**

**NARRATOR (V.O.):**
With sensors in place, you can implement ventilation modes.

In **volume control**, the machine delivers a set tidal volume and lets the pressure be whatever it has to be, up to the safety limit. In **pressure control**, the machine holds a set pressure for a set time, and the volume depends on the lung's compliance.

Then there are **assisted modes**. A patient who is not deeply sedated will try to breathe. When they do, airway pressure dips slightly or flow shifts. A good ventilator detects that effort and synchronizes a supported breath with it.

**[VISUAL: Host on camera.]**

**HOST:**
This is where clinicians pushed back hard on early open-source designs. A machine that only delivers mandatory breaths on a fixed clock requires heavy sedation, and often paralysis. That needs more drugs, which were also in shortage, and it makes it harder to wean the patient off the machine.

Weaning is the whole point. A ventilator buys time for the lungs to heal, and then the patient gradually takes back the work of breathing. If your design can't support spontaneous breathing, it can keep a patient alive but can't easily get them off the machine.

On the control side, most teams used PID controllers, often with feed-forward terms. The challenge is that your "plant" is a human lung whose compliance and resistance vary enormously between patients and change hour by hour in the same patient. The controller has to stay stable across that entire range.

---

## SECTION 6: SAFETY IS THE DESIGN

**[VISUAL: Text on screen: "Assume everything will fail."]**

**NARRATOR (V.O.):**
In consumer electronics, safety is a feature. In a ventilator, safety is the architecture. The guiding principle is that no single fault should be able to harm the patient.

**First, mechanical protection.** There must be a purely mechanical pressure relief valve, a spring-loaded pop-off that opens at a fixed pressure. It doesn't depend on software, sensors, or power. If the firmware crashes with a valve wide open, the relief valve protects the lung.

**Second, a fail-safe state.** If the machine loses power or locks up, the patient should be able to breathe room air through an anti-asphyxia valve, and an alarm that runs independently of the main processor should sound.

**Third, independent monitoring.** Many robust designs use two processors: one controls ventilation, and another watches the first. Add a hardware watchdog timer that forces a reset or alarm if the software stops responding.

**[VISUAL: List of alarms appearing on screen.]**

**NARRATOR (V.O.):**
**Fourth, alarms.** The essentials are:

- High airway pressure, which can mean a blocked tube or a coughing patient.
- Low pressure or low volume, which usually means a disconnection or leak.
- Loss of PEEP.
- Apnea, meaning no breath detected within a set time.
- Power failure and low battery.
- Low oxygen supply.
- Internal technical faults.

**[VISUAL: Host on camera.]**

**HOST:**
Alarm design is harder than it sounds. ICU staff in 2020 were exhausted, working in full protective equipment, often managing far more patients than normal. If your machine alarms constantly for trivial reasons, people start tuning it out. That's alarm fatigue, and it kills. If it fails to alarm when a tube disconnects, that kills too.

The user interface matters for the same reason. Physical knobs, clear labels, and big readable numbers all help. Staff being trained in fifteen minutes during a crisis shouldn't have to navigate nested menus. Several teams made their interface deliberately resemble existing ventilators so clinicians' instincts would carry over.

---

## SECTION 7: THE GAS PATH: OXYGEN, FILTERS, AND HUMIDITY

**[VISUAL: Diagram of the breathing circuit with each component highlighted.]**

**NARRATOR (V.O.):**
Three more issues caught many teams off guard.

**Oxygen is a fire hazard.** High-concentration oxygen makes ordinary materials burn fiercely. Lubricants, some plastics, and sparking brushed motors all become ignition risks. Everything in the gas path must be oxygen-compatible, and the electronics must be isolated from enriched gas.

**The gas path must be clean.** Whatever the patient inhales has passed through your device. 3D-printed parts can be porous and harbor bacteria, and some materials off-gas. Everything in contact with breathing gas needs to be biocompatible and either sterilizable or disposable.

**Exhaled air is infectious.** A COVID patient's exhaled breath carries virus. Vented straight into the room, it endangers the staff. Exhaled gas must pass through a viral filter, and the filter adds resistance that the design has to account for.

Finally, **humidity.** Your nose and throat normally warm and moisten incoming air. An intubated patient bypasses all of that. Dry gas damages the airways and thickens secretions, so the circuit needs a heated humidifier or a heat-and-moisture exchanger. The moisture then affects your flow sensors and can condense in the tubing.

---

## SECTION 8: TESTING AND REGULATION

**[VISUAL: A test lung on a bench, connected to a prototype, waveforms on a monitor.]**

**NARRATOR (V.O.):**
A prototype that works on the bench for an hour proves almost nothing. Verification is where most of the real work is.

Testing starts with a **test lung**, a calibrated device with adjustable compliance and resistance. You test across the full matrix of stiff lungs, compliant lungs, high resistance, and low resistance, at every combination of settings, and compare your readings against a calibrated gas flow analyzer.

Then comes **endurance testing**, which means running continuously for weeks. Motors overheat, bags crack, tubing loosens, and memory leaks finally crash the firmware on day nine.

Then **fault injection**. You deliberately unplug sensors, block tubes, cut power, and corrupt data, and confirm the machine fails safely every time.

**[VISUAL: Logos and document titles: FDA EUA, MHRA RMVS, ISO 80601-2-12, IEC 60601-1, IEC 62304.]**

**NARRATOR (V.O.):**
On the regulatory side, ventilators are normally governed by standards like ISO 80601-2-12 for critical care ventilators, IEC 60601 for electrical safety, and IEC 62304 for medical software. During the pandemic, agencies created faster pathways, such as the FDA's Emergency Use Authorization. Faster did not mean easy. Teams still had to document risk analysis, software validation, and performance testing.

**[VISUAL: Host on camera.]**

**HOST:**
Now for the uncomfortable truth. Of the hundreds of low-cost ventilator projects launched in 2020, only a small fraction received any authorization, and fewer still treated patients.

Part of the reason is good news. Clinical practice evolved. Doctors learned that prone positioning, high-flow oxygen, and non-invasive support could keep many patients off invasive ventilation, and established manufacturers scaled up production.

The other part is that many projects underestimated the problem. They built a mechanism, not a medical device. The projects that succeeded shared a pattern: they had clinicians involved from day one, they started from the regulatory requirements instead of from a clever mechanism, and they had manufacturing partners who knew how to build things reliably at scale.

---

## CLOSING

**[VISUAL: Slow montage of the successful designs, engineers and clinicians working together.]**

**NARRATOR (V.O.):**
So was it all wasted effort? Not at all.

The pandemic ventilator push produced open, well-documented reference designs that still inform work on affordable respiratory care. That matters because the ventilator shortage of 2020 was new only to wealthy countries. In much of the world, there has never been a time when there were enough ventilators. Low-cost, robust, maintainable designs are a permanent need there.

It also trained a generation of engineers in what designing for human life involves: failure modes come before features, the user is an exhausted nurse at 4 a.m., and the simplest-looking problems carry decades of hard-won clinical knowledge.

**[VISUAL: Host on camera.]**

**HOST:**
If you take one thing from this video, make it this: a low-cost ventilator isn't a cheap ventilator. It's one where every dollar was spent on what matters, which is accuracy, reliability, and safety, and nothing was spent on what doesn't.

If you want to go deeper, the MIT Emergency Ventilator documentation, the MHRA's rapidly manufactured ventilator specification, and NASA JPL's published VITAL design are good places to start.

Thanks for watching. If you found this useful, consider subscribing, and I'll see you in the next one.

**[END CARD]**
