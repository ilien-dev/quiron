# Integrating C# .NET and Salesforce's REST API

Salesforce is at the center of a lot of business systems, and sooner or later many .NET developers get asked to connect an application to it. Maybe you need to sync customer data, create leads from a web form, or pull reports into an internal tool. The Salesforce REST API makes all of this possible, and it works nicely with C# once you get past the authentication step.

In this post, I'll walk through how to authenticate with Salesforce, run a query, and create a record, all using `HttpClient` in .NET.

## Step 1: Create a Connected App in Salesforce

Before your application can talk to Salesforce, you need a **Connected App**. This gives you the credentials your code will use.

1. In Salesforce Setup, search for **App Manager** and click **New Connected App**.
2. Give it a name and a contact email.
3. Check **Enable OAuth Settings**.
4. Set a callback URL (for server-to-server integrations, this can be a placeholder like `https://localhost`).
5. Add the OAuth scopes you need, such as **Manage user data via APIs (api)**.
6. Save, then copy the **Consumer Key** and **Consumer Secret**.

It can take a few minutes for a new Connected App to become active, so don't panic if your first request fails.

## Step 2: Authenticate

There are several OAuth flows available. For a backend service, the **Client Credentials flow** is a good fit, since it doesn't require a user to log in interactively. You'll need to enable it on the Connected App and assign a "Run As" user.

Here's a simple class to request an access token:

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

The response includes two important values: the `access_token`, which you'll send with every request, and the `instance_url`, which is the base URL for your org's API. Always use the returned `instance_url` rather than hardcoding one.

## Step 3: Query Records with SOQL

Salesforce uses its own query language, SOQL, which looks a lot like SQL. Let's fetch some accounts:

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

A couple of notes:

- The version number in the URL (`v60.0` here) should match an API version your org supports.
- If a query returns a lot of records, `Done` will be `false` and the response will include a `nextRecordsUrl`. You'll need to follow that URL to get the remaining pages.

## Step 4: Create a Record

Creating records is just a `POST` to the object's endpoint:

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

Salesforce returns the ID of the new record, which you can store for later updates. Updating a record works similarly, using `PATCH` to `/sobjects/Lead/{id}`.

## Tips and Gotchas

- **Handle token expiry.** Access tokens expire. Cache the token, and when you get a `401 Unauthorized`, request a new one and retry.
- **Read the error body.** Salesforce error responses are detailed JSON arrays that tell you exactly which field failed validation. Log them.
- **Watch your API limits.** Every org has a daily API request limit. For bulk operations, look at the Composite API or Bulk API instead of making thousands of individual calls.
- **Use `IHttpClientFactory`.** In ASP.NET Core, register your Salesforce client with dependency injection rather than creating a new `HttpClient` for every request.
- **Keep secrets out of code.** Store your consumer key and secret in user secrets, environment variables, or a vault.

## Wrapping Up

Once you've got authentication working, the Salesforce REST API is straightforward to use from C#. With a Connected App, a token request, and a few `HttpClient` calls, you can query, create, and update records from any .NET application.

From here, you might explore the Composite API for batching requests, or look into Platform Events if you need real-time updates from Salesforce. Happy coding!
