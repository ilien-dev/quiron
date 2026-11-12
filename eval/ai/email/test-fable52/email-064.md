Hi [Name],

I want to flag an issue with the max rate on TW that needs attention this week, and to propose how we resolve it.

**What we're seeing**

Since [date], the max rate applied on TW has not matched what we expect. The configured value is [expected rate], but in practice the system is enforcing [observed rate]. We first noticed this when [how it was detected: a customer report, a monitoring alert, a reconciliation check], and we have since confirmed it in [number] separate cases. The behaviour is consistent and reproducible, so this is not a one-off.

**Impact**

The issue appears to be limited to TW. We ran the same checks on [other markets or environments] and found the correct max rate in each. Within TW, the effect is as follows:

- **Affected volume:** roughly [number or percentage] of [transactions, requests, bookings] since the issue began.
- **Customer impact:** [customers are being capped below the agreed rate, or requests are being rejected once the limit is reached].
- **Financial exposure:** an estimated [amount] to date, growing by about [amount] per day while the issue continues.

These figures are preliminary. I will send confirmed numbers once [team] has finished the full data pull, which I expect by [date].

**Likely cause**

We have not confirmed the root cause yet. The leading explanation is that a configuration change deployed on [date] overwrote the TW-specific value with the global default. The timing matches, and TW is one of the few places where we maintain a local override. Two other possibilities are still open: a currency or unit conversion error in how the rate is calculated, and a stale cached value that was never refreshed after the last update. [Name or team] is working through these and should be able to rule them in or out by [date].

**Proposed next steps**

1. **Immediate fix:** manually restore the TW max rate to [expected rate] as a temporary measure. This is low-risk, can be reversed quickly, and stops the exposure from growing while we investigate.
2. **Root cause:** [team] completes the investigation and shares findings by [date].
3. **Remediation:** once we know the full scope, we identify the affected [customers or transactions] and agree on whether corrections or adjustments are needed.
4. **Prevention:** we add a validation check so that market-specific rate overrides cannot be silently replaced, plus an alert when the applied rate differs from the configured one.

**What I need from you**

- Your approval to apply the temporary fix in step 1. If I have it by [day], we can apply the fix the same day.
- Confirmation of who should own communication with affected customers, if we decide that is necessary.
- Any context on recent TW changes that I may not know about, particularly anything involving rate configuration or [related system].

I'm happy to set up a short call if that is easier than email. Otherwise, I will send an update by [date] with the confirmed figures and the outcome of the investigation.

Thanks,

[Your name]
[Title / Team]

---

I had no background on the issue, so I assumed "TW" is a market (Taiwan) and "max rate" is a configured rate cap. Everything in brackets is a placeholder for your details. If TW or max rate means something else, such as an API rate limit, tell me and I'll adjust the draft.
