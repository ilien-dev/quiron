# Querying a Record Using C# .NET and the Salesforce REST API

Connecting a .NET application to Salesforce often starts with a simple requirement: find a record and use its data. Maybe you need an account’s website, a contact’s email address, or an opportunity’s current stage.

The Salesforce REST API lets you retrieve that information over HTTP. In this tutorial, we’ll query an Account record using C#, `HttpClient`, and Salesforce Object Query Language (SOQL).

## What you’ll need

Before starting, make sure you have:

- A Salesforce org with API access.
- An authenticated user who can read the Account object and requested fields.
- A valid OAuth access token and the `instance_url` returned during authentication.
- A .NET console application.

We’ll assume authentication is already complete. Keep your access token outside source control, and use your organization’s approved OAuth flow to obtain it.

Create the project:

```bash
dotnet new console -n SalesforceRecordQuery
cd SalesforceRecordQuery
```

No additional NuGet packages are required.

## Understand the query endpoint

Salesforce exposes a Query resource that accepts SOQL through the `q` parameter:

```text
GET /services/data/vXX.X/query?q=SOQL_QUERY
```

Requests authenticate with an `Authorization: Bearer` header. The response contains a `records` array alongside metadata describing the result set. See the [Salesforce Query resource documentation](https://developer.salesforce.com/docs/platform/api-rest/guide/resources-query.html).

Our query will retrieve selected fields from one account:

```sql
SELECT Id, Name, Industry, Website
FROM Account
WHERE Id = '001XXXXXXXXXXXXXXX'
LIMIT 1
```

Replace the placeholder with a real Account ID. Selecting explicit fields keeps the response focused and makes the application’s data requirements clear.

## Configure your connection

Set these environment variables before running the application:

```text
SALESFORCE_INSTANCE_URL=https://your-domain.my.salesforce.com
SALESFORCE_ACCESS_TOKEN=your-access-token
SALESFORCE_API_VERSION=vXX.X
SALESFORCE_ACCOUNT_ID=your-account-id
```

Replace `vXX.X` with an API version supported by your org. Use the instance URL supplied by authentication so requests reach the correct Salesforce instance.

## Query the record with C#

Replace `Program.cs` with the following code:

```csharp
using System.Net.Http.Headers;
using System.Text.Json;
using System.Text.RegularExpressions;

static string Required(string name) =>
    Environment.GetEnvironmentVariable(name)
    ?? throw new InvalidOperationException($"Missing {name}.");

var instanceUrl = Required("SALESFORCE_INSTANCE_URL");
var accessToken = Required("SALESFORCE_ACCESS_TOKEN");
var apiVersion = Required("SALESFORCE_API_VERSION");
var accountId = Required("SALESFORCE_ACCOUNT_ID");

// Accept only the expected Salesforce ID format.
if (!Regex.IsMatch(
        accountId, @"\A(?:[A-Za-z0-9]{15}|[A-Za-z0-9]{18})\z"))
{
    throw new ArgumentException("Invalid Salesforce record ID.");
}

var soql =
    "SELECT Id, Name, Industry, Website " +
    $"FROM Account WHERE Id = '{accountId}' LIMIT 1";

var endpoint =
    $"{instanceUrl.TrimEnd('/')}/services/data/{apiVersion}/query" +
    $"?q={Uri.EscapeDataString(soql)}";

using var client = new HttpClient();
using var request = new HttpRequestMessage(HttpMethod.Get, endpoint);

request.Headers.Authorization =
    new AuthenticationHeaderValue("Bearer", accessToken);
request.Headers.Accept.Add(
    new MediaTypeWithQualityHeaderValue("application/json"));

using var response = await client.SendAsync(request);
var body = await response.Content.ReadAsStringAsync();

if (!response.IsSuccessStatusCode)
{
    Console.Error.WriteLine(
        $"Salesforce request failed: {(int)response.StatusCode}");
    return;
}

using var document = JsonDocument.Parse(body);
var records = document.RootElement.GetProperty("records");

if (records.GetArrayLength() == 0)
{
    Console.WriteLine("No matching account was returned.");
    return;
}

var account = records[0];

Console.WriteLine($"ID: {account.GetProperty("Id").GetString()}");
Console.WriteLine($"Name: {account.GetProperty("Name").GetString()}");
Console.WriteLine(
    $"Industry: {account.GetProperty("Industry").GetString()}");
Console.WriteLine(
    $"Website: {account.GetProperty("Website").GetString()}");
```

Run it with:

```bash
dotnet run
```

The program validates the ID’s format, builds the SOQL query, URL-encodes it, and sends an authenticated GET request. It then checks the HTTP status before reading the returned record.

URL encoding protects the request’s structure; it does not prevent SOQL injection. Here, strict validation limits the interpolated value to an alphanumeric record ID. Queries accepting arbitrary text need appropriate SOQL escaping and validation.

## Handle missing records and errors

A successful query can return an empty `records` array. That means no matching account was returned to the authenticated user; it doesn’t necessarily establish whether the record exists elsewhere in the org.

For unsuccessful requests, inspect Salesforce’s error response through controlled diagnostics. Avoid logging access tokens or exposing sensitive response data.

In a production service, reuse `HttpClient` or obtain it through `IHttpClientFactory`, add cancellation support, and handle token expiration through your authentication component.

## When a direct lookup is simpler

Because this example already knows the record ID, you can also retrieve the account directly:

```text
GET /services/data/vXX.X/sobjects/Account/{recordId}?fields=Id,Name,Industry,Website
```

The [sObject Rows resource](https://developer.salesforce.com/docs/platform/api-rest/guide/resources-sobject-retrieve.html) supports retrieval by object and ID. Use SOQL when you need filters or relationship queries.

For queries returning multiple records, follow `nextRecordsUrl` until `done` is true. Salesforce documents that process in its [SOQL query examples](https://developer.salesforce.com/docs/platform/api-rest/guide/dome-query.html).
