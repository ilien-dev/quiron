# ruby-gmail

A Rubyesque interface to Gmail. Connect to Gmail via IMAP and manipulate emails and labels. Send email with your Gmail account via SMTP. Includes full support for parsing and generating MIME messages.

## Features

- **IMAP access**: Connect to your Gmail account, browse mailboxes, search, read, flag, move, and delete messages.
- **Label management**: List, create, rename, apply, and remove Gmail labels.
- **SMTP delivery**: Send plain-text and HTML email, with attachments, through your Gmail account.
- **MIME support**: Parse raw messages into structured objects and generate standards-compliant MIME messages from Ruby.
- **Idiomatic API**: Blocks, chainable queries, and Ruby-style naming throughout.

## Requirements

- Ruby 3.1 or newer
- A Gmail account with IMAP access enabled
- An app password or OAuth2 credentials. Google no longer accepts regular account passwords for IMAP and SMTP login.

## Installation

Add this line to your application's Gemfile:

```ruby
gem "ruby-gmail"
```

Then run:

```sh
bundle install
```

Or install it directly:

```sh
gem install ruby-gmail
```

## Authentication

Gmail requires either an app password (available when 2-Step Verification is enabled on your Google account) or OAuth2. The examples below use an app password loaded from the environment:

```sh
export GMAIL_USERNAME="you@gmail.com"
export GMAIL_APP_PASSWORD="abcd efgh ijkl mnop"
```

Never commit credentials to source control. Store them in environment variables or a secrets manager.

## Quick start

```ruby
require "ruby-gmail"

client = Gmail::Client.new(
  username: ENV.fetch("GMAIL_USERNAME"),
  password: ENV.fetch("GMAIL_APP_PASSWORD")
)

client.connect do |session|
  session.inbox.unread.each do |message|
    puts "#{message.from.first}: #{message.subject}"
  end
end
```

The block form closes the IMAP connection automatically when it finishes.

## Reading mail

```ruby
client.connect do |session|
  session.mailbox("INBOX").search(from: "billing@example.com", since: Date.today - 7).each do |msg|
    puts msg.subject
    puts msg.text_body
    msg.attachments.each { |a| File.binwrite(a.filename, a.content) }
  end
end
```

Search criteria map to IMAP search keys. To use Gmail's native query syntax instead, pass `raw: "has:attachment newer_than:2d"`.

## Working with labels

```ruby
client.connect do |session|
  session.labels.create("Receipts")

  session.inbox.search(subject: "Invoice").each do |msg|
    msg.add_label("Receipts")
    msg.remove_label("INBOX") # archive
  end
end
```

Labels are Gmail's equivalent of folders. A message can carry several labels at once, so `add_label` and `remove_label` do not move the message between mailboxes.

## Sending email

```ruby
client.deliver do |mail|
  mail.to      "friend@example.com"
  mail.subject "Weekly report"
  mail.text    "The report is attached."
  mail.add_file "report.pdf"
end
```

For HTML messages, set `mail.html` in addition to, or instead of, `mail.text`. When both are set, the message is sent as `multipart/alternative`.

## MIME parsing and generation

The MIME layer works on its own, without a network connection.

Parsing raw RFC 822 input:

```ruby
raw = File.read("message.eml")
mail = Gmail::Mime.parse(raw)

mail.headers["Message-ID"]
mail.parts.each do |part|
  puts "#{part.content_type} (#{part.body.bytesize} bytes)"
end
```

Generating a message:

```ruby
mail = Gmail::Mime.build do
  from    "you@gmail.com"
  to      "them@example.com"
  subject "Hello"
  text    "Plain text version"
  html    "<p>HTML version</p>"
end

File.write("out.eml", mail.to_s)
```

The parser handles nested multipart structures, quoted-printable and base64 transfer encodings, RFC 2047 encoded headers, and non-UTF-8 character sets. The generator produces correct boundaries, transfer encodings, and header folding.

## Error handling

All errors inherit from `Gmail::Error`:

- `Gmail::AuthenticationError`: credentials were rejected.
- `Gmail::ConnectionError`: the IMAP or SMTP server could not be reached.
- `Gmail::MimeError`: a message could not be parsed.

```ruby
begin
  client.connect { |s| s.inbox.count }
rescue Gmail::AuthenticationError => e
  warn "Login failed: #{e.message}"
end
```

## Development

```sh
git clone https://github.com/your-org/ruby-gmail.git
cd ruby-gmail
bundle install
bundle exec rake test
```

Tests that touch the live Gmail service are skipped unless `GMAIL_TEST_USERNAME` and `GMAIL_TEST_APP_PASSWORD` are set. Unit tests run offline against recorded fixtures.

## Contributing

1. Fork the repository and create a feature branch.
2. Add tests for your change.
3. Run `bundle exec rake` and confirm it passes.
4. Open a pull request describing the change and its motivation.

## License

Released under the MIT License. See `LICENSE` for details.
