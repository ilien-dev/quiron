# The Wild SQL Query I Wrote For Work This Week

The ticket sounded harmless:

> “Can we show how many minutes each customer’s integrations were disconnected, broken down by hour?”

Sure. We have connection events. We have timestamps. PostgreSQL has subtraction.

I figured this was an afternoon task.

Then I opened the data.

One integration could have several overlapping disconnection records. Some records were duplicates. Some incidents were still open. Some started before the reporting window and ended inside it. And if two integrations were disconnected simultaneously, the customer should only accumulate one minute of downtime per minute.

Oh, and the chart needed to include hours with zero downtime.

What eventually emerged was a SQL query with a running window aggregate, a second window function, several CTEs, and enough timestamp arithmetic that I briefly considered changing careers.

The interesting part wasn’t making the query complicated. It was figuring out which complications were actually necessary.

## The innocent-looking table

Here’s a simplified version of the table:

```sql
CREATE TABLE integration_outages (
    id           bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    customer_id  bigint NOT NULL,
    started_at   timestamptz NOT NULL,
    ended_at     timestamptz,
    CHECK (ended_at IS NULL OR ended_at >= started_at)
);
```

Each row represents a period when an integration was disconnected. A null `ended_at` means the outage is ongoing.

For this report, “customer downtime” meant any time when **at least one integration was disconnected**. That definition matters. A report measuring complete service failure would need different logic.

Suppose one customer has these outages:

```text
Integration A: 09:10 ───────────── 09:40
Integration B:       09:25 ───────────── 09:55
```

Adding their durations gives us 60 minutes.

But the customer experienced 45 minutes of downtime: 09:10 through 09:55.

We needed the duration of the **union of the intervals**, not the sum of their individual durations.

That was the first point where my afternoon task started developing a personality.

## My first attempt was subtly wrong

I knew this was a gaps-and-islands problem: identify overlapping intervals, group them, and collapse each group into one continuous interval.

My first instinct was to compare each outage’s start against the previous outage’s end:

```sql
LAG(ended_at) OVER (
    PARTITION BY customer_id
    ORDER BY started_at
)
```

If the current start came after the previous end, I’d found a new group.

Reasonable. Readable. Wrong.

Consider these intervals:

```text
A: 09:00 ───────────────────────────── 12:00
B:       09:30 ── 09:45
C:                    10:00 ── 10:15
```

For interval C, `LAG()` returns B’s end: 09:45.

C starts at 10:00, so that comparison claims there’s a gap.

But A is still running. All three intervals belong to the same island.

The question isn’t:

> Did the immediately preceding row end?

It’s:

> Did every preceding interval end before this one started?

That requires the **maximum end timestamp across all preceding rows**.

This one detail is the heart of the query.

## The query

The report takes a customer ID and two timestamps. The reporting window is half-open: `[from, to)`. An outage ending exactly at the start contributes nothing; one starting exactly at the end also contributes nothing.

For this version, the parameters must describe a nonempty window with UTC hour-aligned boundaries. That keeps every output bucket a complete, elapsed hour. The application validates those inputs.

Here’s the PostgreSQL query:

```sql
WITH
params AS (
    SELECT
        $1::bigint      AS customer_id,
        $2::timestamptz AS report_from,
        $3::timestamptz AS report_to,
        statement_timestamp() AS as_of
),

clipped AS (
    SELECT
        o.id,
        GREATEST(o.started_at, p.report_from) AS start_at,
        LEAST(
            COALESCE(o.ended_at, p.as_of),
            p.report_to
        ) AS end_at
    FROM integration_outages o
    CROSS JOIN params p
    WHERE o.customer_id = p.customer_id
      AND o.started_at < p.report_to
      AND COALESCE(o.ended_at, p.as_of) > p.report_from
),

valid_intervals AS (
    SELECT *
    FROM clipped
    WHERE start_at < end_at
),

frontiers AS (
    SELECT
        *,
        MAX(end_at) OVER (
            ORDER BY start_at, end_at, id
            ROWS BETWEEN UNBOUNDED PRECEDING
                     AND 1 PRECEDING
        ) AS previous_max_end
    FROM valid_intervals
),

marked AS (
    SELECT
        *,
        CASE
            WHEN previous_max_end IS NULL
              OR start_at > previous_max_end
            THEN 1
            ELSE 0
        END AS starts_island
    FROM frontiers
),

numbered AS (
    SELECT
        *,
        SUM(starts_island) OVER (
            ORDER BY start_at, end_at, id
            ROWS BETWEEN UNBOUNDED PRECEDING
                     AND CURRENT ROW
        ) AS island_id
    FROM marked
),

merged AS (
    SELECT
        island_id,
        MIN(start_at) AS start_at,
        MAX(end_at)   AS end_at
    FROM numbered
    GROUP BY island_id
),

hours AS (
    SELECT
        h AS hour_start,
        h + INTERVAL '1 hour' AS hour_end
    FROM params p
    CROSS JOIN LATERAL generate_series(
        p.report_from,
        p.report_to - INTERVAL '1 hour',
        INTERVAL '1 hour'
    ) AS buckets(h)
)

SELECT
    h.hour_start,
    COALESCE(
        SUM(
            EXTRACT(
                EPOCH FROM (
                    LEAST(m.end_at, h.hour_end)
                    - GREATEST(m.start_at, h.hour_start)
                )
            ) / 60.0
        ),
        0
    ) AS downtime_minutes
FROM hours h
LEFT JOIN merged m
    ON m.start_at < h.hour_end
   AND m.end_at > h.hour_start
GROUP BY h.hour_start
ORDER BY h.hour_start;
```

Yes, that is a lot of SQL for a chart.

But each stage has one job.

## Clip first, think second

The `clipped` CTE trims every incident to the reporting window.

If an outage started yesterday and we’re reporting on today, yesterday’s portion doesn’t belong in the calculation. Similarly, an outage extending beyond the report gets cut off at the report’s end.

Open incidents end at `as_of`, captured using `statement_timestamp()`. That gives the report one consistent definition of “now,” anchored to the start of the statement.

This also means future hours show zero rather than projecting an ongoing outage indefinitely into the future.

After clipping, `valid_intervals` removes empty intervals.

Doing this early makes everything downstream easier. The merge logic only sees intervals that can actually contribute to the answer.

## The running frontier

The `frontiers` CTE calculates the furthest endpoint reached by any earlier interval:

```sql
MAX(end_at) OVER (
    ORDER BY start_at, end_at, id
    ROWS BETWEEN UNBOUNDED PRECEDING
             AND 1 PRECEDING
)
```

The frame is important.

If it included the current row, the maximum would include the interval we’re trying to classify. Since an interval ends after it starts, that would undermine the comparison.

The ordering is explicit and deterministic, including `id` as a final tie-breaker. Both window calculations use the same ordering.

Now we can mark a new island whenever the current interval begins beyond that running frontier.

I used `>` rather than `>=`, so touching intervals merge:

```text
09:00–09:30
09:30–10:00
```

There’s no positive-duration gap between them. Treating them as one interval preserves the result and reduces the number of rows.

## Turning flags into groups

Once each row has a `starts_island` value of either zero or one, a running sum produces group identifiers:

```text
starts_island: 1 0 0 1 0 1
island_id:     1 1 1 2 2 3
```

That’s the second window function.

Then `merged` groups by the identifier and takes the earliest start and latest end.

Duplicates disappear into the same island. Nested intervals work. Chains of overlapping intervals work.

At this point, we finally have the thing we originally wanted: disjoint periods of customer downtime.

Only now is it safe to add durations.

## The chart still needs its empty hours

Aggregating outage rows alone can’t produce an hour with no outages. There’s no row to aggregate.

So `hours` generates the reporting timeline independently. The final query starts from those buckets and left-joins the merged downtime intervals.

The overlap predicate is:

```sql
m.start_at < h.hour_end
AND m.end_at > h.hour_start
```

For each matching pair, the intersection starts at the later start and ends at the earlier end.

Subtract those timestamps, convert seconds to minutes, and sum.

Because the downtime intervals have already been merged, their intersections cannot double-count time. Each full hour therefore lands between zero and 60 minutes.

That upper bound became a useful sanity check.

## The cases that earned their tests

The happy path barely tested anything interesting. The cases that mattered were:

- Identical duplicate intervals.
- One long interval containing several short ones.
- Overlap chains where the first and last intervals never touch.
- Incidents crossing the report boundaries.
- Open incidents.
- Incidents ending exactly on an hour boundary.
- A customer with no incidents at all.

The nested-interval case caught my `LAG()` mistake immediately.

For additional confidence, I compared generated examples against a small application implementation that sorted and merged intervals. Independent implementations gave me more confidence than a test that repeated the SQL’s logic.

Performance still needed checking against realistic data. CTEs made the query readable; they didn’t automatically make it fast. I inspected the execution plan and how many historical rows the initial filter examined.

## What I actually learned

The hardest part wasn’t window-function syntax.

It was translating “downtime per hour” into precise rules about overlap, missing endpoints, boundaries, and empty results.

Once those rules were explicit, the query became a sequence of manageable transformations.

I still wouldn’t call it a small query.

But I can explain every CTE, test every boundary, and trace a suspicious chart value back to the intervals that produced it.

For something that began with “just subtract the timestamps,” I’ll take that.
