# share-button

> :warning: :warning: **Currently Unmaintained** :warning: :warning:
>
> This project is no longer actively developed. Issues and pull requests may not receive a response, and some network integrations may have broken as third-party APIs changed. Use at your own risk, or consider forking.

Fast, beautiful, and painless social shares.

## Why share-button?

Most social sharing widgets load a pile of third-party scripts, slow your page down, track your visitors, and look out of place next to your design. share-button takes a different approach:

- **Fast.** No external scripts are loaded until a visitor actually chooses to share, so there is no impact on page load time.
- **Beautiful.** A single, clean button that expands to reveal the networks you have enabled. It looks good by default and is easy to restyle.
- **Painless.** Drop in one element, call one constructor, and you are done. Sensible defaults are pulled from your page's meta tags.
- **Private.** No tracking pixels or iframes are injected into your page.

## Installation

Install with npm:

```bash
npm install share-button --save
```

Or download the compiled script and stylesheet from the `dist` folder and include them directly:

```html
<link rel="stylesheet" href="share-button.min.css">
<script src="share-button.min.js"></script>
```

## Usage

Add the element wherever you want the button to appear:

```html
<share-button></share-button>
```

Then initialize it:

```js
var ShareButton = require('share-button');

new ShareButton();
```

That's it. With no configuration, the button shares the current page URL and uses your page's title, description, and Open Graph image.

## Configuration

Pass an options object to customize behavior globally or per network:

```js
new ShareButton({
  url: 'https://example.com/my-post',
  title: 'A post worth sharing',
  description: 'A short summary of the post.',
  image: 'https://example.com/images/cover.png',
  ui: {
    flyout: 'top center',
    buttonText: 'Share'
  },
  networks: {
    twitter: {
      enabled: true,
      description: 'Custom text for the tweet'
    },
    facebook: {
      enabled: true,
      appId: 'YOUR_APP_ID'
    },
    pinterest: {
      enabled: false
    },
    email: {
      enabled: true,
      title: 'Thought you might like this'
    }
  }
});
```

### Global options

| Option | Default | Description |
| --- | --- | --- |
| `url` | Current page URL | The URL to share |
| `title` | Page `<title>` | The title of the shared content |
| `description` | Meta description | The text accompanying the share |
| `image` | Open Graph image | The image used by networks that support one |
| `ui.flyout` | `top center` | The direction in which network icons expand |
| `ui.buttonText` | `Share` | The label on the button |

### Supported networks

Twitter, Facebook, Pinterest, Reddit, LinkedIn, WhatsApp, and email. Each network accepts `enabled`, plus overrides for `url`, `title`, `description`, and `image` where applicable. Any network set to `enabled: false` is hidden from the button.

### Hooks

Each network accepts `before` and `after` callbacks, which are useful for analytics or for changing the share content at the last moment:

```js
new ShareButton({
  networks: {
    twitter: {
      before: function (element) {
        this.description = 'Shared from ' + element.dataset.section;
      },
      after: function () {
        console.log('Tweet dialog opened');
      }
    }
  }
});
```

## Styling

The default stylesheet is intentionally small. Override its classes in your own CSS, or skip the bundled stylesheet entirely and write your own. Multiple buttons on one page can be styled and configured independently by passing a selector as the first argument:

```js
new ShareButton('.footer-share', { ui: { flyout: 'bottom center' } });
```

## Browser support

share-button works in current versions of Chrome, Firefox, Safari, and Edge. Because the project is unmaintained, compatibility with newer browser releases has not been verified.

## Contributing

This project is not being maintained, so contributions are unlikely to be reviewed or merged. If you depend on share-button, forking the repository is the most reliable path forward. If you are interested in taking over maintenance, open an issue to start the conversation.

## License

Released under the [MIT License](LICENSE).
