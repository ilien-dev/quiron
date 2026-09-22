# Integrating C# .NET and Salesforce's REST API

Salesforce sits in the middle of a lot of business systems, and sooner or later a .NET developer gets asked to connect an app to it. Maybe you need to sync customer data. Maybe it's creating leads from a web form, or pulling reports into an internal tool. The Salesforce REST API can do all of it, and it works nicely with C# once you get past authentication.

In this post I'll walk through how to authenticate with Salesforce, run a query and create a record, all with `HttpClient` in .NET.

## Step 1: Create a Connected App in Salesforce

Before your application can talk to Salesforce you need a Connected App. It provides the credentials your application will use.

1. In Salesforce Setup, search for **App Manager** and click **New Connected App**.
2. Give it a name and a contact email.
3. Check **Enable OAuth Settings**.
4. Set a callback URL (for server-to-server integrations, this can be a placeholder like `https://localhost`).
5. Add the OAuth scopes you need, such as **Manage user data via APIs (api)**.
6. Save, then copy the **Consumer Key** and **Consumer Secret**.

A new Connected App can take a few minutes to become active. Don't panic if your first request fails.

## Step 2: Authenticate

There are several OAuth flows. For a backend service I'd pick the Client Credentials flow, since nobody has to log in interactively. You'll need to enable it on the Connected App and assign a "Run As" user.

Here's a small class that requests an access token. I've kept it minimal:

```csharp
using System.Net.Http;
using System.Net.Http.Json;
using System.Text.Json.Serialization;

public class SalesforceAuthResponse
{
    [JsonPropertyName("access_token")]
    public string AccessToken { get; set; }

    [JsonPropertyName("instance_url")]
    public string InstanceUrl { get; set; }
}

public class SalesforceAuthenticator
{
    private readonly HttpClient _http;

    public SalesforceAuthenticator(HttpClient http) => _http = http;

    public async Task<SalesforceAuthResponse> GetTokenAsync(
        string domain, string clientId, string clientSecret)
    {
        var content = new FormUrlEncodedContent(new Dictionary<string, string>
        {
            ["grant_type"] = "client_credentials",
            ["client_id"] = clientId,
            ["client_secret"] = clientSecret
        });

        var response = await _http.PostAsync(
            $"https://{domain}/services/oauth2/token", content);

        response.EnsureSuccessStatusCode();
        return await response.Content.ReadFromJsonAsync<SalesforceAuthResponse>();
    }
}
```

The response has two values you care about. The `access_token` is sent with every request. The `instance_url` is the base URL for your org's API, and you should always use the one that comes back instead of hardcoding it.

## Step 3: Query records with SOQL

Salesforce has its own query language, SOQL, and it looks a lot like SQL. Let's fetch some accounts:

```csharp
public class Account
{
    public string Id { get; set; }
    public string Name { get; set; }
    public string Industry { get; set; }
}

public class QueryResult<T>
{
    public int TotalSize { get; set; }
    public bool Done { get; set; }
    public List<T> Records { get; set; }
}

public async Task<List<Account>> GetAccountsAsync(SalesforceAuthResponse auth)
{
    var soql = "SELECT Id, Name, Industry FROM Account LIMIT 10";
    var url = $"{auth.InstanceUrl}/services/data/v60.0/query?q={Uri.EscapeDataString(soql)}";

    var request = new HttpRequestMessage(HttpMethod.Get, url);
    request.Headers.Authorization =
        new AuthenticationHeaderValue("Bearer", auth.AccessToken);

    var response = await _http.SendAsync(request);
    response.EnsureSuccessStatusCode();

    var result = await response.Content.ReadFromJsonAsync<QueryResult<Account>>(
        new JsonSerializerOptions { PropertyNameCaseInsensitive = true });

    return result.Records;
}
```

Two things I'd point out here. The version number in the URL (`v60.0` here) should match an API version your org supports. And if a query returns a lot of records, `Done` will be `false` and the response will include a `nextRecordsUrl`, which you'll need to follow to get the rest of the pages.

## Step 4: Create a record

Creating a record is just a `POST` to the object's endpoint, so this one is shorter:

```csharp
public async Task<string> CreateLeadAsync(SalesforceAuthResponse auth)
{
    var lead = new
    {
        FirstName = "Jane",
        LastName = "Doe",
        Company = "Example Corp",
        Email = "jane.doe@example.com"
    };

    var request = new HttpRequestMessage(
        HttpMethod.Post,
        $"{auth.InstanceUrl}/services/data/v60.0/sobjects/Lead/")
    {
        Content = JsonContent.Create(lead)
    };
    request.Headers.Authorization =
        new AuthenticationHeaderValue("Bearer", auth.AccessToken);

    var response = await _http.SendAsync(request);
    var body = await response.Content.ReadAsStringAsync();

    if (!response.IsSuccessStatusCode)
        throw new Exception($"Salesforce error: {body}");

    using var doc = JsonDocument.Parse(body);
    return doc.RootElement.GetProperty("id").GetString();
}
```

Salesforce returns the ID of the new record. It should be stored somewhere if you plan to update the record later. Updates work the same way, with a `PATCH` to `/sobjects/Lead/{id}`.

## Tips and gotchas

- Access tokens expire. Cache the token, and when you get a `401 Unauthorized`, request a new one and retry.
- Read the error body. Salesforce error responses are detailed JSON arrays that tell you exactly which field failed validation. Log them.
- Watch your API limits. Every org has a daily API request limit. For bulk operations, look at the Composite API or the Bulk API before you make thousands of single calls.
- In ASP.NET Core, use `IHttpClientFactory` and register your Salesforce client with dependency injection. Don't create a new `HttpClient` for every request.
- Keep secrets out of code. The consumer key and secret belong in user secrets, environment variables or a vault.

## Wrapping up

Authentication is the hard part. Once that works, the Salesforce REST API is fairly easy to use from C#: a Connected App, a token request and a few `HttpClient` calls, and you can query, create and update records from any .NET application.

If I were going further, I'd look at the Composite API for batching requests, or at Platform Events if you need real-time updates from Salesforce. Happy coding!
