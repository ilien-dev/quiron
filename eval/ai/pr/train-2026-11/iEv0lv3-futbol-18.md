## Team Season Collection and CSV.foreach

### Summary

This PR adds a `TeamSeasonCollection` class to group game data by team and season, and switches CSV loading from `CSV.read` to `CSV.foreach`. Together these changes make season-level statistics easier to compute and reduce memory use when loading the larger data files.

### Changes

**New: `TeamSeasonCollection`**
- Added `lib/team_season_collection.rb`, which builds team-season objects from `game_teams.csv` joined with season data from `games.csv`.
- Each team-season tracks wins, losses, ties, goals, shots, and tackles for one team in one season.
- Season-based methods such as `winningest_coach`, `worst_coach`, `most_accurate_team`, `least_accurate_team`, `most_tackles`, and `fewest_tackles` can now read from pre-grouped data. They no longer need to re-filter every game on each call.
- Added `test/team_season_collection_test.rb` with fixture data covering grouping, aggregation, and edge cases such as seasons with no games for a team.

**Refactor: `CSV.foreach`**
- Replaced `CSV.read(...).map` with `CSV.foreach(path, headers: true, header_converters: :symbol)` in all collection classes.
- Rows are now streamed one at a time instead of loading the whole file into an array first. This reduces peak memory, mainly for `game_teams.csv`.
- Behavior is unchanged, and existing collection tests pass without modification.

### Testing

- Run `rake test` or `ruby -Itest test/*_test.rb`.
- All existing tests pass, and the new tests cover `TeamSeasonCollection`.
- Spot-checked season stats against the full data set to confirm the results match the previous implementation.

### Notes for Reviewers

- Please check the season-join logic in `TeamSeasonCollection#build`, since it depends on `game_id` matching between files.
- A follow-up PR could move the remaining league-wide methods onto this collection as well.

---

I don't have access to the repo here, so the file names, method names, and test details above are assumptions based on the standard futbol project structure. Please adjust them to match the actual diff before posting.
