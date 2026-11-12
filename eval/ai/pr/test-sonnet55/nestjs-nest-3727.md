## PR Checklist

Please check if your PR fulfills the following requirements:

- [x] The commit message follows our guidelines: https://github.com/nestjs/nest/blob/master/CONTRIBUTING.md
- [x] Tests for the changes have been added (for bug fixes / features)
- [ ] Docs have been added / updated (for bug fixes / features)

## PR Type

What kind of change does this PR introduce?

- [ ] Bugfix
- [x] Feature
- [ ] Code style update (formatting, local variables)
- [ ] Refactoring (no functional changes, no api changes)
- [ ] Build related changes
- [ ] CI related changes
- [ ] Other... Please describe:

## What is the current behavior?

When a global prefix is set via `app.setGlobalPrefix()`, it is applied to every route in the application. The only way to opt specific routes out is the `exclude` option on `setGlobalPrefix()`, which requires listing each path or route info centrally. This is awkward for controllers that should never be prefixed (health checks, webhooks, well-known endpoints), because the exclusion lives far from the controller it affects and must be kept in sync manually.

## What is the new behavior?

`@Controller()` now accepts a `useGlobalPrefix` option in its `ControllerOptions`. It defaults to `true`, so existing behavior is unchanged.

```ts
@Controller({ path: 'health', useGlobalPrefix: false })
export class HealthController {
  @Get()
  check() {
    return 'ok';
  }
}
```

With `app.setGlobalPrefix('api')`:

- `GET /health` resolves for `HealthController`
- `GET /api/health` is not registered for it
- All other controllers continue to resolve under `/api`

The option is stored as controller metadata and read by the router when the global prefix is applied, alongside the existing `exclude` handling. Both mechanisms can be used together.

## Does this PR introduce a breaking change?

- [ ] Yes
- [x] No

Default is `true`, so no migration is needed for existing applications.

## Other information

Unit tests cover the default case, the opt-out case, and the combination with `exclude`. Documentation in the `nestjs/docs.nestjs.com` repository still needs a follow-up PR, so that box is left unchecked.
