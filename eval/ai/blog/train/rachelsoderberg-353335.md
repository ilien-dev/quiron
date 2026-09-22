# Querying a Record Using C# .NET and the Salesforce REST API

Salesforce’s REST API makes it straightforward to retrieve CRM data from a .NET application. In this tutorial, we’ll query a single `Account` record using C#, `HttpClient`, and Salesforce Object Query Language—better known as SOQL.

We’ll assume that your application has already completed an OAuth flow and received:

- An access token
- Your Salesforce instance URL, such as `https://your-domain.my.salesforce.com`

Never hard-code production credentials. Store them in a secret manager, environment variables, or another secure configuration provider.

## The Salesforce query endpoint

SOQL queries are sent to this endpoint:

```text
{instanceUrl}/services/data/{apiVersion}/query?q={soqlQuery}
```

For example, the following SOQL query retrieves one account by ID:

```sql
SELECT Id, Name, Industry, Phone
FROM Account
WHERE Id = '001XXXXXXXXXXXXXXX'
LIMIT 1
```

Although Salesforce IDs contain only a restricted set of characters, query parameters should always be URL-encoded before being added to the request URI.

## Define the response models

A Salesforce query response contains metadata and an array named `records`. We can model the relevant fields with C# classes:

```csharp
using System.Text.Json.Serialization;

public sealed class SalesforceQueryResponse<T>
{
    [JsonPropertyName("totalSize")]
    public int TotalSize { get; set; }

    [JsonPropertyName("done")]
    public bool Done { get; set; }

    [JsonPropertyName("records")]
    public List<T> Records { get; set; } = [];
}

public sealed class AccountRecord
{
    [JsonPropertyName("Id")]
    public string Id { get; set; } = string.Empty;

    [JsonPropertyName("Name")]
    public string Name { get; set; } = string.Empty;

    [JsonPropertyName("Industry")]
    public string? Industry { get; set; }

    [JsonPropertyName("Phone")]
    public string? Phone { get; set; }
}
```

Salesforce also returns an `attributes` object for each record. You can omit it when you do not need it because `System.Text.Json` ignores unmatched properties by default.

## Create the query method

The following method sends the request, checks the HTTP response, and returns either the matching account or `null`:

```csharp
using System.Net.Http.Headers;
using System.Text.Json;

public sealed class SalesforceClient
{
    private readonly HttpClient _httpClient;
    private readonly string _instanceUrl;
    private readonly string _apiVersion;

    public SalesforceClient(
        HttpClient httpClient,
        string instanceUrl,
        string apiVersion = "vXX.X")
    {
        _httpClient = httpClient;
        _instanceUrl = instanceUrl.TrimEnd('/');
        _apiVersion = apiVersion;
    }

    public async Task<AccountRecord?> GetAccountAsync(
        string accountId,
        string accessToken,
        CancellationToken cancellationToken = default)
    {
        const string fields = "Id, Name, Industry, Phone";

        string escapedId = accountId.Replace("'", "\\'");
        string soql =
            $"SELECT {fields} FROM Account " +
            $"WHERE Id = '{escapedId}' LIMIT 1";

        string requestUrl =
            $"{_instanceUrl}/services/data/{_apiVersion}/query" +
            $"?q={Uri.EscapeDataString(soql)}";

        using var request = new HttpRequestMessage(
            HttpMethod.Get,
            requestUrl);

        request.Headers.Authorization =
            new AuthenticationHeaderValue("Bearer", accessToken);

        using HttpResponseMessage response =
            await _httpClient.SendAsync(request, cancellationToken);

        string json =
            await response.Content.ReadAsStringAsync(cancellationToken);

        if (!response.IsSuccessStatusCode)
        {
            throw new HttpRequestException(
                $"Salesforce returned {(int)response.StatusCode}: {json}");
        }

        var result =
            JsonSerializer.Deserialize<
                SalesforceQueryResponse<AccountRecord>>(json);

        return result?.Records.FirstOrDefault();
    }
}
```

Replace `vXX.X` with an API version supported by your Salesforce organization. Keeping the version configurable makes future upgrades easier.

## Register and use the client

In an ASP.NET Core application, register `SalesforceClient` through the built-in HTTP client factory:

```csharp
builder.Services.AddHttpClient<SalesforceClient>();
```

You can then inject and call it from a service or controller:

```csharp
AccountRecord? account = await salesforceClient.GetAccountAsync(
    "001XXXXXXXXXXXXXXX",
    accessToken,
    cancellationToken);

if (account is null)
{
    Console.WriteLine("Account not found.");
    return;
}

Console.WriteLine($"{account.Name} - {account.Industry}");
```

A successful Salesforce query may return zero records, so treating “not found” as `null` is usually more useful than throwing an exception.

## Querying by record ID without SOQL

When you already know both the object type and record ID, Salesforce also provides an sObject endpoint:

```text
GET /services/data/{apiVersion}/sobjects/Account/{recordId}
```

You can restrict the returned data with a `fields` query parameter:

```text
?sfields=...
```

In practice, use the endpoint’s documented `fields` parameter:

```text
?fields=Id,Name,Industry,Phone
```

This approach is concise for direct ID lookups. SOQL is more flexible when records must be found using external IDs, names, dates, relationships, or multiple conditions.

## Production considerations

Before shipping, account for token expiration, transient failures, rate limits, and Salesforce’s structured error responses. Reuse `HttpClient` through dependency injection, pass cancellation tokens, and avoid logging access tokens or sensitive record data.

Also remember that Salesforce applies the authenticated user’s permissions. A valid query can still fail—or omit inaccessible fields—when the user lacks object, record, or field-level access.

With authentication, careful response handling, and a small typed client, Salesforce queries fit naturally into modern C# applications.