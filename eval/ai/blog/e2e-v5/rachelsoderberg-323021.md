# Integrating C# .NET and Salesforce's REST API

*This is the first post in my Salesforce REST API Services series, which follows my earlier series on the Salesforce SOAP API. The SOAP API works, but not every stack or team can deal with SOAP, so I wanted to go through the same ground again with REST. The examples are in C# .NET Core and also work in .NET Framework, and the Salesforce screens are from Lightning Experience, Spring 2020 release.*

Today we're only going to get as far as logging in: setting up the Connected App in Salesforce and getting an access token back from it in our .NET application. Everything else in the series depends on that token, so it's worth getting right before we try to do anything with records.

# Create a Connected App

Before your application can talk to Salesforce, it needs a Connected App. This is where the credentials your code will use come from. I recommend doing this in your Test or Dev org first and only setting it up in Production once everything works.

1. In Setup, go to Apps > App Manager and click New Connected App.
2. Give it a name and a contact email.
3. Check Enable OAuth Settings.
4. Enter a callback URL. This can be a dummy value like `https://localhost`, because we're using the [resource owner password grant](https://tools.ietf.org/html/rfc6749#section-4.3) and Salesforce never redirects anyone to it.
5. Add the OAuth scope "Access and manage your data (api)".
6. Save, then copy the Consumer Key and Consumer Secret.

Write the Consumer Key and Secret down somewhere safe right away. They're only shown once. And it takes several minutes for a new Connected App to become active, so wait a bit before you use it. If your first request fails straight after saving, that's probably why.

# Authenticate

To log in we send a POST to the token endpoint. For a sandbox that's `https://test.salesforce.com/services/oauth2/token`. The body has to be `FormUrlEncodedContent`, because that's what Salesforce requires, and it carries the grant type, the Consumer Key and Secret from the Connected App, and the username and password of the Salesforce user we're logging in as.

```csharp
using System.Net;
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
        string clientId, string clientSecret, string username, string password)
    {
        ServicePointManager.SecurityProtocol =
            SecurityProtocolType.Tls11 | SecurityProtocolType.Tls12;

        var content = new FormUrlEncodedContent(new Dictionary<string, string>
        {
            ["grant_type"] = "password",
            ["client_id"] = clientId,
            ["client_secret"] = clientSecret,
            ["username"] = username,
            ["password"] = password
        });

        var response = await _http.PostAsync(
            "https://test.salesforce.com/services/oauth2/token", content);

        response.EnsureSuccessStatusCode();
        return await response.Content.ReadFromJsonAsync<SalesforceAuthResponse>();
    }
}
```

The credentials have to be stored securely. Don't put them in your code or commit them anywhere.

If it works, the response gives you two values we'll use for the rest of the series: the `access_token`, which I store as AuthToken and send with every request, and the `instance_url`, which I store as ServiceUrl. Every call after this one goes to the ServiceUrl plus the API endpoint, `/services/data/v36.0/` in my case (use the version your org is on). Don't hardcode the instance URL, always take the one Salesforce sends back. (Any sample values from my org in this series have been altered, so don't try to use them.)

# When it doesn't work

A few errors you might hit, and what to check:

- A bad request usually means something is wrong with the body. Check your `FormUrlEncodedContent` first.
- A security error means .NET isn't using a TLS version Salesforce accepts. The `ServicePointManager.SecurityProtocol` line at the top of `GetTokenAsync` adds TLS 1.1 and 1.2.
- `invalid_client_id` means the user you're logging in as can't see the Connected App. Check that the user's Profile has your Connected App listed under Connected App Access.

Once you have an AuthToken back, you're logged in. In the next post we'll use it to query an Account from our org.

---

If you'd like to catch up with me on social media, come find me over on [Twitter](https://twitter.com/RachSoderberg) or [LinkedIn](https://www.linkedin.com/in/rachelsoderberg/) and say hello!
