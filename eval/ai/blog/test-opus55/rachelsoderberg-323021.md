# Integrating C# .NET and Salesforce's REST API

Sooner or later, many .NET developers have to connect an application to Salesforce. You might be syncing customers from an internal system, pushing orders into a CRM, or building a reporting service. Salesforce has SOAP, Bulk, and Streaming APIs, but for most integrations the **REST API** is the simplest choice.

This post walks through a minimal, production-friendly setup: authenticating with OAuth 2.0, running SOQL queries, creating records, and handling errors. It uses only `HttpClient` and `System.Text.Json`, with no third-party SDK.

## Step 1: Set Up a Connected App

Salesforce needs to know about your application before it will issue tokens. In Setup, create an **External Client App** (or a classic Connected App in older orgs) and:

1. Enable OAuth settings.
2. Enable the **Client Credentials Flow**.
3. Assign a **Run As** user. Every API call will execute with this user's permissions.
4. Copy the **Consumer Key** and **Consumer Secret**.

The client credentials flow suits server-to-server integrations because no user has to log in interactively. If you need per-user access, use the Web Server flow instead.

> Keep the secret out of source control. Use User Secrets locally and a vault such as Azure Key Vault in production.

## Step 2: Model the Configuration

```csharp
public sealed class SalesforceOptions
{
    public required string LoginUrl { get; init; }   // https://yourdomain.my.salesforce.com
    public required string ClientId { get; init; }
    public required string ClientSecret { get; init; }
    public string ApiVersion { get; init; } = "v62.0";
}
```

Put the API version in configuration so you can upgrade it without a code change. Salesforce releases a new version three times a year.

## Step 3: Get an Access Token

The token endpoint returns an `access_token` and an `instance_url`. Send all later requests to that instance URL.

```csharp
public sealed record TokenResponse(
    [property: JsonPropertyName("access_token")] string AccessToken,
    [property: JsonPropertyName("instance_url")] string InstanceUrl);

public async Task<TokenResponse> AuthenticateAsync(CancellationToken ct = default)
{
    var form = new FormUrlEncodedContent(new Dictionary<string, string>
    {
        ["grant_type"] = "client_credentials",
        ["client_id"] = _options.ClientId,
        ["client_secret"] = _options.ClientSecret
    });

    using var response = await _http.PostAsync(
        $"{_options.LoginUrl}/services/oauth2/token", form, ct);

    response.EnsureSuccessStatusCode();
    return (await response.Content.ReadFromJsonAsync<TokenResponse>(ct))!;
}
```

Cache the token and request a new one only when an API call returns `401 Unauthorized`. Calling the token endpoint before every request is slow, and it can also hit rate limits.

## Step 4: Query Data with SOQL

The `/query` endpoint takes a SOQL string and returns a paged result. Here's a generic wrapper:

```csharp
public sealed record QueryResult<T>(
    [property: JsonPropertyName("totalSize")] int TotalSize,
    [property: JsonPropertyName("done")] bool Done,
    [property: JsonPropertyName("nextRecordsUrl")] string? NextRecordsUrl,
    [property: JsonPropertyName("records")] List<T> Records);

public async Task<List<T>> QueryAsync<T>(string soql, CancellationToken ct = default)
{
    var results = new List<T>();
    var url = $"/services/data/{_options.ApiVersion}/query?q={Uri.EscapeDataString(soql)}";

    while (url is not null)
    {
        var page = await SendAsync<QueryResult<T>>(HttpMethod.Get, url, null, ct);
        results.AddRange(page.Records);
        url = page.Done ? null : page.NextRecordsUrl;
    }

    return results;
}
```

Salesforce returns at most 2,000 records per page by default, so the loop follows `nextRecordsUrl` until `done` is `true`. Usage stays clean:

```csharp
public sealed record Account(string Id, string Name, string? Industry);

var accounts = await sf.QueryAsync<Account>(
    "SELECT Id, Name, Industry FROM Account WHERE CreatedDate = LAST_N_DAYS:7");
```

**Watch out for SOQL injection.** If a query includes user input, escape single quotes and backslashes, or validate the input against an allow-list.

## Step 5: Create and Update Records

Writes go through the `/sobjects` endpoint:

```csharp
public sealed record CreateResponse(string Id, bool Success);

public Task<CreateResponse> CreateAsync(string sObject, object record, CancellationToken ct = default) =>
    SendAsync<CreateResponse>(HttpMethod.Post,
        $"/services/data/{_options.ApiVersion}/sobjects/{sObject}", record, ct);

public Task UpdateAsync(string sObject, string id, object fields, CancellationToken ct = default) =>
    SendAsync<object>(HttpMethod.Patch,
        $"/services/data/{_options.ApiVersion}/sobjects/{sObject}/{id}", fields, ct);
```

Updates use `PATCH` and return `204 No Content`, so check for an empty body before you deserialize.

## Step 6: Centralize Requests and Errors

When a request fails, Salesforce returns a JSON array of errors:

```json
[{ "message": "Required fields are missing: [Name]", "errorCode": "REQUIRED_FIELD_MISSING" }]
```

A single `SendAsync` method can attach the token, retry once after a `401`, and turn failures into meaningful exceptions:

```csharp
private async Task<T> SendAsync<T>(HttpMethod method, string path, object? body, CancellationToken ct, bool retried = false)
{
    _token ??= await AuthenticateAsync(ct);

    using var request = new HttpRequestMessage(method, _token.InstanceUrl + path);
    request.Headers.Authorization = new("Bearer", _token.AccessToken);
    if (body is not null) request.Content = JsonContent.Create(body);

    using var response = await _http.SendAsync(request, ct);

    if (response.StatusCode == HttpStatusCode.Unauthorized && !retried)
    {
        _token = null;
        return await SendAsync<T>(method, path, body, ct, retried: true);
    }

    if (!response.IsSuccessStatusCode)
    {
        var error = await response.Content.ReadAsStringAsync(ct);
        throw new SalesforceException(response.StatusCode, error);
    }

    if (response.StatusCode == HttpStatusCode.NoContent) return default!;
    return (await response.Content.ReadFromJsonAsync<T>(ct))!;
}
```

Register the client with `IHttpClientFactory` (`services.AddHttpClient<SalesforceClient>()`) so connection pooling and DNS refresh work correctly. You can add Polly or `Microsoft.Extensions.Http.Resilience` for transient failure handling.

## Tips From the Trenches

- **Monitor API limits.** Each response includes a `Sforce-Limit-Info` header showing your daily usage. Log it.
- **Batch when you can.** The Composite API (`/composite/sobjects`) creates up to 200 records in one call.
- **Use the Bulk API 2.0** for anything over a few thousand records.
- **Grant minimal permissions.** The Run As user should have only the permissions the integration needs.

## Wrapping Up

You don't need a heavy SDK to work with Salesforce from .NET. A small client built on `HttpClient` covers authentication, querying, writes, and error handling, and you control every request it makes. Start with the pieces above, add resilience policies, and you'll have an integration that is easy to test and maintain.

What does your Salesforce integration stack look like? Let me know in the comments!
