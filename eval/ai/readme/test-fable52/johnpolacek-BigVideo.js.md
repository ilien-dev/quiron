# BigVideo.js

The jQuery Plugin for Big Background Video (and Images)

BigVideo.js makes it easy to add fit-to-fill background video to websites. It can play silent ambient background video (or a series of videos), or it can act as a player for a video playlist. It can also show big background images, which is handy as a fallback on devices that don't autoplay ambient video.

## Dependencies

BigVideo.js relies on a few other libraries:

- [jQuery](http://jquery.com)
- [jQuery UI](http://jqueryui.com) (for the slider control)
- [Video.js](http://videojs.com)
- [imagesLoaded](https://github.com/desandro/imagesloaded)

## Installation

Install with Bower:

```
bower install BigVideo.js
```

Or download the files and include them yourself, along with the dependencies:

```html
<link rel="stylesheet" href="css/bigvideo.css">

<script src="js/jquery.min.js"></script>
<script src="js/jquery-ui.min.js"></script>
<script src="js/jquery.imagesloaded.min.js"></script>
<script src="js/video.js"></script>
<script src="js/bigvideo.js"></script>
```

## Usage

### Basic setup

Create a BigVideo object, initialize it, and show a video:

```js
$(function() {
    var BV = new $.BigVideo();
    BV.init();
    BV.show('http://video-js.zencoder.com/oceans-clip.mp4');
});
```

### Alternate formats

No single format plays in every browser. Pass an alternate source so browsers without MP4 support still get a video:

```js
BV.show('vids/river.mp4', { altSource: 'vids/river.ogv' });
```

### Ambient video

For silent, looping background video, use the `ambient` option:

```js
BV.show('vids/river.mp4', { ambient: true });
```

### Playlists

Pass an array of videos to play them in sequence:

```js
BV.show(['vids/river.mp4', 'vids/forest.mp4', 'vids/coast.mp4']);
```

Playlists work in ambient mode too:

```js
BV.show(['vids/river.mp4', 'vids/forest.mp4'], { ambient: true });
```

### Background images

Pass an image path instead of a video and BigVideo.js will show it fit-to-fill:

```js
BV.show('img/background.jpg');
```

### Touch devices

Most mobile devices do not autoplay video, so ambient video won't work there. Detect touch support (for example with [Modernizr](http://modernizr.com)) and show an image instead:

```js
var BV = new $.BigVideo();
BV.init();

if (Modernizr.touch) {
    BV.show('img/background.jpg');
} else {
    BV.show('vids/river.mp4', { ambient: true });
}
```

## Options

Pass an options object when you create the BigVideo object:

```js
var BV = new $.BigVideo({
    useFlashForFirefox: true,
    forceAutoplay: false,
    controls: false,
    doLoop: false,
    container: $('body'),
    shrinkable: false
});
```

| Option | Default | Description |
| --- | --- | --- |
| `useFlashForFirefox` | `true` | Uses the Flash fallback in Firefox so MP4 files play. Set to `false` if you supply an Ogg or WebM alternate source. |
| `forceAutoplay` | `false` | Starts playback immediately, without waiting for user interaction. |
| `controls` | `false` | Shows the player controls. |
| `doLoop` | `false` | Loops the video when it ends. |
| `container` | `$('body')` | The element the video is placed in. |
| `shrinkable` | `false` | When `true`, the video scales down to fit the container rather than always filling it. |

## Accessing the player

BigVideo.js is built on Video.js. To get at the underlying player and its API, use `getPlayer`:

```js
var player = BV.getPlayer();
player.pause();
```

Any Video.js method or event is available this way, so you can add custom controls, listen for playback events, or adjust the volume.

## Tips

- Keep video files small. Background video should be compressed heavily; a dark overlay or pattern on top hides most artifacts.
- Strip the audio track from ambient video to save bandwidth.
- Always provide an image fallback for devices that can't autoplay.
- Check that text over the video stays readable throughout the clip.

## Browser support

BigVideo.js works in current versions of Chrome, Firefox, Safari, and Internet Explorer, with a Flash fallback through Video.js for older browsers. Touch devices fall back to images as described above.

## Contributing

Bug reports and pull requests are welcome. Please open an issue describing the problem or the proposed change before submitting large changes, and keep pull requests focused on a single fix or feature.

## License

BigVideo.js is released under the MIT License.
