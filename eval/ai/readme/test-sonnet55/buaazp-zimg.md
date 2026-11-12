# zimg

A lightweight, high-performance image storage and processing system.

zimg stores images and serves them in whatever size, format, and quality your application asks for, without a heavyweight media pipeline. Upload an image once, then request any variant through a simple URL.

## Features

- **Fast by design**: small memory footprint, low-latency reads, and concurrent request handling.
- **On-the-fly processing**: resize, crop, rotate, convert format, and adjust quality per request.
- **Smart caching**: processed variants are cached so repeated requests are served directly from storage.
- **Content-addressed storage**: identical uploads are deduplicated automatically using a content hash.
- **Simple HTTP API**: upload, fetch, and delete with plain HTTP calls and no SDK required.
- **Pluggable backends**: store files on local disk or an S3-compatible object store.
- **Format support**: JPEG, PNG, GIF, WebP, and AVIF.

## Quick Start

### Requirements

- A recent Linux, macOS, or Windows machine
- A C/C++ toolchain or the prebuilt release binary
- Optional: Docker

### Install

Download a release binary, or build from source:

```bash
git clone https://github.com/<your-org>/zimg.git
cd zimg
make build
```

Or run with Docker:

```bash
docker run -p 4869:4869 -v ./data:/var/lib/zimg zimg/zimg:latest
```

### Run

```bash
./zimg --config ./conf/zimg.conf
```

The server listens on port `4869` by default.

## Usage

### Upload an image

```bash
curl -X POST --data-binary @photo.jpg \
  -H "Content-Type: image/jpeg" \
  http://localhost:4869/upload
```

The response contains the image's unique ID:

```json
{ "ok": true, "id": "5f1c0a9e3b7d2c48a6e1" }
```

### Fetch an image

```
GET /5f1c0a9e3b7d2c48a6e1
```

### Request a processed variant

Add query parameters to transform the image on demand:

```
GET /5f1c0a9e3b7d2c48a6e1?w=400&h=300&fit=cover&fmt=webp&q=80
```

| Parameter | Description                                  |
|-----------|----------------------------------------------|
| `w`       | Target width in pixels                       |
| `h`       | Target height in pixels                      |
| `fit`     | Resize mode: `cover`, `contain`, or `fill`   |
| `fmt`     | Output format: `jpeg`, `png`, `webp`, `avif` |
| `q`       | Quality, from 1 to 100                       |
| `rot`     | Rotation in degrees (90, 180, 270)           |

### Delete an image

```bash
curl -X DELETE http://localhost:4869/5f1c0a9e3b7d2c48a6e1
```

## Configuration

Configuration lives in `conf/zimg.conf`. Common options:

```ini
[server]
port = 4869
workers = 8

[storage]
backend = disk            ; disk | s3
path = /var/lib/zimg

[cache]
enabled = true
max_size = 2GB

[limits]
max_upload_size = 20MB
max_dimension = 8192
```

Every option can also be set through an environment variable prefixed with `ZIMG_`, for example `ZIMG_SERVER_PORT=8080`.

## Architecture

zimg has three layers:

1. **API layer** handles HTTP requests and validates input.
2. **Processing layer** decodes, transforms, and re-encodes images.
3. **Storage layer** persists originals and cached variants on the configured backend.

Originals are never modified. Every variant is derived from the stored original and cached by its parameters.

## Performance

zimg is built to stay small and quick. Variants are cached after first use, large uploads are streamed rather than buffered in memory, and processing runs on a bounded worker pool to keep resource use predictable under load. Run `make bench` to benchmark on your own hardware.

## Security

- Enforce upload size and dimension limits to prevent abuse.
- Place zimg behind a reverse proxy for TLS and authentication.
- Restrict the upload and delete endpoints to trusted clients.

## Development

```bash
make test      # run the test suite
make lint      # run static checks
make bench     # run benchmarks
```

## Contributing

Contributions are welcome. Open an issue to discuss larger changes first, then submit a pull request with tests covering your change.

## License

Released under the MIT License. See [LICENSE](LICENSE) for details.
