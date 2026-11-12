Salesforce has SDKs and community libraries for .NET, but you often don't need them. The REST API is plain HTTPS and JSON, and modern .NET ships with everything required: `HttpClient`, `System.Text.Json`, and async streams. In this post we'll authenticate, query, and write records using nothing but the base class library.

## Prerequisites

- .NET 8 or later
- A Salesforce org (a free Developer Edition works)
- A Connected App (or External Client App) with the **Client Credentials Flow** enabled and a "Run As" user assigned

Older tutorials use the username-password OAuth flow. Salesforce discourages it and blocks it by default in newer orgs, so for server-to-server integrations use client credentials or the JWT bearer flow instead.

## Step 1: Get an access token

The client credentials flow is a single POST to your org's My Domain URL:

```csharp
public sealed record SalesforceToken(
    [property: JsonPropertyName("access_token")] string AccessToken,
    [property: JsonPropertyName("instance_url")] string InstanceUrl);

public static async Task<SalesforceToken> GetTokenAsync(
    HttpClient http, string domain, string clientId, string clientSecret)
{
    var form = new FormUrlEncodedContent(new Dictionary<string, string>
    {
        ["grant_type"] = "client_credentials",
        ["client_id"] = clientId,
        ["client_secret"] = clientSecret
    });

    using var response = await http.PostAsync(
        $"{domain}/services/oauth2/token", form);
    response.EnsureSuccessStatusCode();

    return (await response.Content.ReadFromJsonAsync<SalesforceToken>())!;
}
```

Here `domain` looks like `https://yourcompany.my.salesforce.com`. Keep the client secret in user secrets, environment variables, or a vault, never in source control.

The response gives you two things that matter: the `access_token` and the `instance_url`. Send all later calls to the instance URL, not to a hardcoded host.

## Step 2: Configure the API client

```csharp
var token = await GetTokenAsync(authClient, domain, clientId, clientSecret);

var api = new HttpClient { BaseAddress = new Uri(token.InstanceUrl) };
api.DefaultRequestHeaders.Authorization =
    new AuthenticationHeaderValue("Bearer", token.AccessToken);
```

In a real application, register this through `IHttpClientFactory` rather than creating clients by hand, and put token handling in a `DelegatingHandler`.

## Step 3: Query records with SOQL

Queries go to the `/query` endpoint with URL-encoded SOQL. Salesforce returns results in pages. When `done` is `false`, the response includes a `nextRecordsUrl` to follow. An `IAsyncEnumerable` hides that paging from callers:

```csharp
public sealed record QueryResult<T>(
    int TotalSize, bool Done, string? NextRecordsUrl, List<T> Records);

public sealed record Account(string Id, string Name, string? Industry);

public static async IAsyncEnumerable<T> QueryAsync<T>(
    HttpClient api, string soql)
{
    string? url = $"/services/data/v65.0/query?q={Uri.EscapeDataString(soql)}";

    while (url is not null)
    {
        var page = await api.GetFromJsonAsync<QueryResult<T>>(url);
        foreach (var record in page!.Records)
            yield return record;

        url = page.Done ? null : page.NextRecordsUrl;
    }
}
```

Usage:

```csharp
await foreach (var account in QueryAsync<Account>(api,
    "SELECT Id, Name, Industry FROM Account WHERE Industry != null"))
{
    Console.WriteLine($"{account.Name} ({account.Industry})");
}
```

`GetFromJsonAsync` uses case-insensitive matching by default, so `totalSize` binds to `TotalSize` without attributes. If you build SOQL from user input, escape it carefully, because SOQL injection is a real risk.

## Step 4: Create and update records

Creating a record is a POST to the sObject's endpoint:

```csharp
var newAccount = new Dictionary<string, object>
{
    ["Name"] = "Contoso Ltd",
    ["Industry"] = "Technology"
};

using var created = await api.PostAsJsonAsync(
    "/services/data/v65.0/sobjects/Account", newAccount);
created.EnsureSuccessStatusCode();

var result = await created.Content.ReadFromJsonAsync<JsonElement>();
var id = result.GetProperty("id").GetString();
```

I used a dictionary here deliberately. `PostAsJsonAsync` camel-cases property names by default, which would turn an anonymous object's `Name` into `name`. Dictionary keys are sent exactly as written, which also suits custom fields like `Region__c`.

Updates use PATCH against the record ID and return `204 No Content` on success:

```csharp
using var updated = await api.PatchAsJsonAsync(
    $"/services/data/v65.0/sobjects/Account/{id}",
    new Dictionary<string, object> { ["Industry"] = "Finance" });
updated.EnsureSuccessStatusCode();
```

Send only the fields you want to change.

## Step 5: Handle errors properly

`EnsureSuccessStatusCode` is fine for demos, but Salesforce error bodies are worth reading. They come back as a JSON array:

```json
[{ "message": "Required fields are missing: [Name]",
   "errorCode": "REQUIRED_FIELD_MISSING",
   "fields": ["Name"] }]
```

Deserialize the array and include it in your exceptions or logs. Two cases need specific handling:

- **401 with `INVALID_SESSION_ID`**: the token expired. Request a new one and retry the call once. The client credentials flow issues no refresh token, so you simply authenticate again.
- **403 with `REQUEST_LIMIT_EXCEEDED`**: you've hit the org's daily API limit. Every response carries a `Sforce-Limit-Info` header (for example `api-usage=42/15000`), so you can monitor usage before it becomes an outage.

## Production tips

- **Pin the API version** (`v65.0` here) in one constant and upgrade it deliberately.
- **Batch your calls.** The Composite API bundles multiple operations into one request, and Bulk API 2.0 is the right tool for tens of thousands of records.
- **Add resilience.** `Microsoft.Extensions.Http.Resilience` gives you retries and circuit breakers with a few lines of configuration.
- **Use a least-privilege integration user.** The "Run As" user's permissions define what your app can touch.

## Wrapping up

With one token request and a configured `HttpClient`, you can query, create, and update Salesforce data from C#. From here, look at upserts via external IDs, the Composite API, and Change Data Capture if you need Salesforce to push changes to you.
