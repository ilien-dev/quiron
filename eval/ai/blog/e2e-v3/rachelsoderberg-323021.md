# Integrating C# .NET and Salesforce's REST API

Sooner or later a lot of .NET developers get asked to hook an application up to Salesforce. Maybe it's syncing customer data, or creating leads from a web form, or pulling reports into an internal tool. The REST API can do all of that and it works nicely with C#, though getting authentication right is the hard part. Below I go from a token to a query to a new record, all with plain `HttpClient`.

## Create a Connected App

Your code needs credentials before it can talk to Salesforce, and those come from a **Connected App**.

1. In Salesforce Setup, search for **App Manager** and click **New Connected App**.
2. Give it a name and a contact email.
3. Check **Enable OAuth Settings**.
4. Set a callback URL (for server-to-server integrations, this can be a placeholder like `https://localhost`).
5. Add the OAuth scopes you need, such as **Manage user data via APIs (api)**.
6. Save, then copy the **Consumer Key** and **Consumer Secret**.

A new Connected App can take a few minutes to become active, so if your first request fails, wait a bit before you start debugging.

## Get a token

Salesforce has several OAuth flows. For a backend service I'd use the **Client Credentials flow** because nobody has to log in interactively. You have to enable it on the Connected App and assign a "Run As" user.

This class requests an access token:

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

Two values in the response matter: the `access_token` goes out with every request, and the `instance_url` is the base URL for your org's API, so use the one you get back and don't hardcode it.

## Query records with SOQL

Salesforce has its own query language called SOQL, which looks a lot like SQL. Here's a query that fetches some accounts:

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

The version number in the URL (`v60.0` here) has to be one your org supports. And if a query returns a lot of records, `Done` will be `false` and the response will carry a `nextRecordsUrl`. You follow that URL to get the rest of the pages.

## Creating and updating records

To create one you `POST` to the object's endpoint:

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

Salesforce sends back the ID of the new record, which you can keep for later updates. An update works similarly, with a `PATCH` to `/sobjects/Lead/{id}`.

## Things that will bite you

Access tokens expire, so cache the token, and when you get a `401 Unauthorized` just request a new one and retry.

Read the error body, too. Salesforce errors come back as detailed JSON arrays that tell you exactly which field failed validation, so log them.

Every org has a daily limit on API requests. For bulk work use the Composite API or the Bulk API instead of making thousands of single calls.

In ASP.NET Core, register your Salesforce client with dependency injection through `IHttpClientFactory` instead of creating a new `HttpClient` for every request.

And keep the consumer key and secret out of your code. User secrets, environment variables or a vault are all fine.

If you want to go further, the Composite API is there for batching requests and Platform Events are there if you need real-time updates from Salesforce.
