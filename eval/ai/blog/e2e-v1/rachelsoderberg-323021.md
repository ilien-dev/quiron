# Integrating C# .NET and Salesforce's REST API

Salesforce sits in the middle of a lot of business systems, and sooner or later many .NET developers get asked to connect an application to it. Maybe you need to sync customer data or create leads from a web form, or maybe someone wants reports pulled out of Salesforce and into one of your internal tools. The Salesforce REST API can do all of that, and it works nicely with C# once you get past authentication.

I'll go through authenticating with Salesforce, running a query and creating a record, all with `HttpClient` in .NET.

## Step 1: Create a Connected App in Salesforce

Before your application can talk to Salesforce you need a **Connected App**. That is where the credentials for your code come from.

1. In Salesforce Setup, search for **App Manager** and click **New Connected App**.
2. Give it a name and a contact email.
3. Check **Enable OAuth Settings**.
4. Set a callback URL (for server-to-server integrations, this can be a placeholder like `https://localhost`).
5. Add the OAuth scopes you need, such as **Manage user data via APIs (api)**.
6. Save, then copy the **Consumer Key** and **Consumer Secret**.

A new Connected App can take a few minutes to become active, so don't panic if your first request fails.

## Step 2: Authenticate

Salesforce offers several OAuth flows. For a backend service the **Client Credentials flow** is a good fit, because nobody has to log in interactively. You'll need to enable it on the Connected App and assign a "Run As" user.

Here's a small class that requests an access token:

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

Two values in the response matter. The `access_token` goes out with every request. The `instance_url` is the base URL for your org's API, and you should always use the one that comes back instead of hardcoding it.

## Step 3: Query records with SOQL

Salesforce has its own query language, SOQL. It looks a lot like SQL. Here's a query for some accounts:

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

Two things to watch:

- The version number in the URL (`v60.0` here) should match an API version your org supports.
- If a query returns a lot of records, `Done` will be `false` and the response will have a `nextRecordsUrl`. Follow that URL to get the rest of the pages.

## Step 4: Create a record

To create a record you `POST` to the object's endpoint:

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

Salesforce sends back the ID of the new record. Store it if you plan to update the record later (updates work the same way, with a `PATCH` to `/sobjects/Lead/{id}`).

## Tips and gotchas

- **Handle token expiry.** Access tokens expire. Cache the token, and when you get a `401 Unauthorized` request a new one and retry.
- **Read the error body.** Salesforce errors come back as detailed JSON arrays that tell you exactly which field failed validation. Log them.
- **Watch your API limits.** Every org has a daily API request limit. For bulk operations, look at the Composite API or Bulk API instead of making thousands of individual calls.
- **Use `IHttpClientFactory`.** In ASP.NET Core, register your Salesforce client with dependency injection. Don't create a new `HttpClient` for every request.
- **Keep secrets out of code.** Put your consumer key and secret in user secrets or environment variables, or in a vault.

## Where to go next

Once authentication works, the rest of the API is straightforward to use from C#. The Composite API is worth a look if you want to batch requests, and Platform Events if you need real-time updates from Salesforce. Happy coding!
