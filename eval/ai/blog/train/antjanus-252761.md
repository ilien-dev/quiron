# The Wild SQL Query I Wrote For Work This Week

Most SQL queries begin innocently.

You need a few columns. Maybe a `JOIN`. Perhaps a `GROUP BY` if you’re feeling adventurous.

Then someone says:

> “Can we also show the most recent status, except when the account was reactivated, and calculate usage against the plan that was active at the time?”

That is how a query stops being a query and becomes a small software system written entirely in common table expressions.

This week, I wrote one of those queries.

The task sounded simple: build a report showing customer accounts that exceeded their monthly usage allowance. For each account, the report needed to include:

- The plan active during that billing month
- The allowance included with that plan
- Total billable usage
- Usage that occurred during free trial periods
- Credits issued after billing
- The account’s latest status
- The first timestamp at which it exceeded its allowance
- Its longest continuous streak of over-limit days

There were a few complications.

Plans can change mid-month. Usage events can arrive late. Credits are stored separately. Accounts can be suspended, reopened, and suspended again. Trials can overlap calendar months. Some historical plan records overlap because of an old migration bug.

Oh, and the query needed to run against PostgreSQL without creating temporary tables.

Perfect.

## The data model

The important tables looked approximately like this:

```sql
accounts (
  id,
  name,
  created_at
)

account_status_events (
  account_id,
  status,
  occurred_at
)

plan_history (
  account_id,
  plan_id,
  valid_from,
  valid_until
)

plans (
  id,
  name,
  monthly_allowance
)

usage_events (
  id,
  account_id,
  units,
  occurred_at,
  received_at
)

trial_periods (
  account_id,
  starts_at,
  ends_at
)

usage_credits (
  account_id,
  billing_month,
  units
)
```

The report accepted a billing month and returned one row per account.

At first glance, this seems like a collection of ordinary joins. The difficulty is that nearly every relationship depends on time.

A usage event belongs to the plan active when the event occurred, not necessarily the account’s current plan. An event is free if it occurred during a trial, regardless of when it was received. The account status must reflect the latest status event. Credits apply to a billing month rather than a specific usage event.

That meant I couldn’t just join everything and aggregate. Doing so would multiply rows and inflate totals.

Instead, I built the result in stages.

## Step one: define the month once

The query begins with a tiny parameter CTE:

```sql
WITH params AS (
  SELECT
    DATE '2026-08-01' AS month_start,
    DATE '2026-08-01' + INTERVAL '1 month' AS month_end
)
```

This seems trivial, but it prevents date-boundary logic from being copied throughout the query.

I consistently used a half-open interval:

```sql
occurred_at >= month_start
AND occurred_at < month_end
```

This avoids awkward expressions involving `23:59:59.999999` and works correctly regardless of timestamp precision.

## Step two: repair overlapping plan history

The old migration bug had produced overlapping plan records. If I joined usage directly to `plan_history`, one event could match multiple plans.

I needed a deterministic rule: when multiple plan records match, use the one with the latest `valid_from`.

PostgreSQL’s `LATERAL` join was perfect for this:

```sql
usage_with_plan AS (
  SELECT
    u.id,
    u.account_id,
    u.units,
    u.occurred_at,
    selected_plan.plan_id,
    selected_plan.monthly_allowance
  FROM usage_events u
  CROSS JOIN params p
  JOIN LATERAL (
    SELECT
      ph.plan_id,
      pl.monthly_allowance
    FROM plan_history ph
    JOIN plans pl ON pl.id = ph.plan_id
    WHERE ph.account_id = u.account_id
      AND ph.valid_from <= u.occurred_at
      AND (
        ph.valid_until IS NULL
        OR ph.valid_until > u.occurred_at
      )
    ORDER BY ph.valid_from DESC, ph.plan_id DESC
    LIMIT 1
  ) selected_plan ON TRUE
  WHERE u.occurred_at >= p.month_start
    AND u.occurred_at < p.month_end
)
```

A lateral join allows the subquery to reference columns from the row on its left. Conceptually, PostgreSQL runs the subquery for each usage event and selects its best matching plan.

The second sort key, `plan_id`, is there to make the result deterministic even if two records share the same `valid_from`.

Is this compensating for broken historical data? Yes.

Should the underlying data also be fixed? Absolutely.

But reporting queries often need to survive reality before reality can be repaired.

## Step three: remove trial usage without multiplying rows

An account can have multiple trial periods. Joining trials directly to usage could duplicate events when bad data contains overlapping trials.

I didn’t need information about the matching trial. I only needed to know whether one existed.

That called for `EXISTS`:

```sql
classified_usage AS (
  SELECT
    uwp.*,
    EXISTS (
      SELECT 1
      FROM trial_periods tp
      WHERE tp.account_id = uwp.account_id
        AND tp.starts_at <= uwp.occurred_at
        AND tp.ends_at > uwp.occurred_at
    ) AS is_trial
  FROM usage_with_plan uwp
)
```

This is one of my favorite SQL habits: if the question is “does a related row exist?”, use `EXISTS` instead of joining and cleaning up duplicates later.

Now each usage event still appeared exactly once.

## Step four: calculate daily totals

The final report needed both monthly usage and consecutive over-limit days. That meant I first needed daily usage:

```sql
daily_usage AS (
  SELECT
    account_id,
    occurred_at::date AS usage_date,
    SUM(units) FILTER (WHERE NOT is_trial) AS billable_units,
    MAX(monthly_allowance) AS allowance
  FROM classified_usage
  GROUP BY account_id, occurred_at::date
)
```

The `FILTER` clause keeps conditional aggregation readable. The more portable version would be:

```sql
SUM(CASE WHEN NOT is_trial THEN units ELSE 0 END)
```

Both work, but `FILTER` expresses the intent directly.

The `MAX(monthly_allowance)` deserves scrutiny. If plans change within a day, taking the maximum is not necessarily correct. In our system, plan changes become effective at midnight, so every event on a given date should have the same allowance.

I added a separate data-quality check to verify that assumption. Production SQL is full of statements that are correct only because of business invariants. Those invariants should be explicit somewhere.

## Step five: find the first over-limit moment

Daily totals were not precise enough to identify the first event that crossed the allowance.

For that, I used a cumulative window function:

```sql
running_usage AS (
  SELECT
    account_id,
    id AS usage_event_id,
    occurred_at,
    units,
    monthly_allowance,
    SUM(units) OVER (
      PARTITION BY account_id
      ORDER BY occurred_at, id
      ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW
    ) AS cumulative_units
  FROM classified_usage
  WHERE NOT is_trial
),
first_overage AS (
  SELECT DISTINCT ON (account_id)
    account_id,
    occurred_at AS first_overage_at
  FROM running_usage
  WHERE cumulative_units > monthly_allowance
  ORDER BY account_id, occurred_at, usage_event_id
)
```

The explicit `ROWS` frame matters.

Without it, PostgreSQL may use a peer-aware frame in which rows sharing the same ordering value are considered together. Since multiple usage events can have identical timestamps, adding the event ID and specifying `ROWS` ensures the running total advances one event at a time.

Then `DISTINCT ON` selects the earliest qualifying event per account.

`DISTINCT ON` is PostgreSQL-specific, but it is wonderfully concise for “first row in each group” problems.

## Step six: calculate the longest streak

This was the fun part.

We needed the longest sequence of consecutive calendar days during which an account remained above its allowance.

After producing one row per over-limit day, I used the classic gaps-and-islands technique:

```sql
over_limit_days AS (
  SELECT
    account_id,
    usage_date
  FROM daily_usage
  WHERE billable_units > allowance
),
numbered_days AS (
  SELECT
    account_id,
    usage_date,
    usage_date
      - ROW_NUMBER() OVER (
          PARTITION BY account_id
          ORDER BY usage_date
        )::integer AS island_key
  FROM over_limit_days
),
streaks AS (
  SELECT
    account_id,
    COUNT(*) AS streak_length
  FROM numbered_days
  GROUP BY account_id, island_key
),
longest_streak AS (
  SELECT
    account_id,
    MAX(streak_length) AS longest_over_limit_streak
  FROM streaks
  GROUP BY account_id
)
```

Why does subtracting the row number work?

Imagine these dates:

```text
2026-08-03
2026-08-04
2026-08-05
2026-08-09
```

Their row numbers are `1`, `2`, `3`, and `4`. Subtracting those values from the dates gives the same result for the first three consecutive dates, but a different result for August 9.

That calculated value becomes an identifier for each “island” of consecutive dates.

It looks like sorcery the first time you see it. Then it becomes a tool you keep finding excuses to use.

## Step seven: obtain the current status

The latest status per account was another first-row-per-group problem:

```sql
latest_status AS (
  SELECT DISTINCT ON (account_id)
    account_id,
    status
  FROM account_status_events
  ORDER BY account_id, occurred_at DESC
)
```

In the real query, I added the status event’s primary key as a final sort key. Timestamps are rarely as unique as we pretend they are.

## Step eight: assemble the report

After separately aggregating usage and credits, the final query became pleasantly boring:

```sql
SELECT
  a.id,
  a.name,
  ls.status,
  mu.billable_units,
  COALESCE(c.credit_units, 0) AS credit_units,
  mu.billable_units - COALESCE(c.credit_units, 0) AS net_units,
  fo.first_overage_at,
  COALESCE(lst.longest_over_limit_streak, 0) AS longest_over_limit_streak
FROM accounts a
JOIN monthly_usage mu ON mu.account_id = a.id
LEFT JOIN latest_status ls ON ls.account_id = a.id
LEFT JOIN monthly_credits c ON c.account_id = a.id
LEFT JOIN first_overage fo ON fo.account_id = a.id
LEFT JOIN longest_streak lst ON lst.account_id = a.id
WHERE mu.billable_units - COALESCE(c.credit_units, 0) > mu.allowance
ORDER BY net_units DESC;
```

That was the reward for building everything in layers: the final assembly read like a description of the report.

The complete query was much longer—roughly 180 lines with comments—but no individual section was especially mysterious.

## What I learned

The hardest part wasn’t SQL syntax. It was preserving the grain of the data.

A usage row is one event. A daily aggregate is one account-date pair. A credit row is one account-month pair. A status result is one account. Joining two datasets before reducing them to compatible grains can quietly duplicate values while still producing believable output.

That is more dangerous than a query that crashes.

A few principles kept this one under control:

- Define time boundaries once and use half-open intervals.
- Use `EXISTS` when you only need to test for related data.
- Aggregate independent one-to-many relationships before joining them.
- Add deterministic tie-breakers to window functions and `DISTINCT ON`.
- State the business assumptions hidden inside aggregate functions.
- Treat each CTE as a transformation with a clearly defined row grain.
- Test pathological cases, not just typical accounts.

I tested accounts with no usage, only trial usage, overlapping trials, duplicate timestamps, mid-month plan changes, late-arriving events, no status history, multiple credits, and usage exactly equal to the allowance.

The query is wild, but it is not wild because it uses obscure syntax.

It is wild because a seemingly simple business question contained years of product decisions, data migrations, billing rules, and edge cases.

That is what I enjoy about SQL. A good query is not merely a request for data. It is an executable explanation of how the business believes its own history should be interpreted.

Sometimes that explanation fits on five lines.

Sometimes it becomes a small novel with twelve CTEs, three window functions, a lateral join, and a gaps-and-islands trick.

This week, I got the novel.