# ketama

**C library for consistent hashing, and language bindings**

ketama is a small C library for mapping keys to servers with consistent hashing. It was built for distributing keys across a pool of memcached servers. It works with any system where you need to spread data across nodes and keep reshuffling small when nodes are added or removed.

## Why consistent hashing?

The naive way to pick a server is `hash(key) % number_of_servers`. It works until the pool changes. Add or remove one server and almost every key maps to a different place. For a cache, that means a sudden flood of misses that can overload your backend.

With consistent hashing, changing the pool remaps only a small fraction of keys, roughly `1/n` of the keyspace for `n` servers. All other keys stay on the server they were already on.

## How it works

1. Each server in your pool is hashed many times, using variations of its address, to produce a set of points on a circle (the *continuum*).
2. Each server gets a number of points proportional to its weight, so higher-capacity servers receive a larger share of keys.
3. To find a key's server, ketama hashes the key with MD5, finds its position on the circle, and walks clockwise to the nearest server point.
4. The continuum is sorted, so a lookup is a fast binary search.

Adding a server inserts new points into the circle. The new server takes over only the keys that fall just before those points. Removing a server sends its keys to the next points clockwise. No other keys move.

## Server list format

ketama reads its server pool from a plain text file. Each line holds an `address:port`, a tab, and a weight. The weight is typically the server's memory in megabytes.

```
# ketama.servers
10.0.1.1:11211	600
10.0.1.2:11211	300
10.0.1.3:11211	200
```

Lines beginning with `#` are comments. If you change the file, ketama rebuilds the continuum the next time it is loaded. The continuum can be stored in shared memory, so several processes on the same host can share one copy.

## Building

The core library has no dependencies beyond a standard C toolchain.

```sh
cd libketama
make
sudo make install
```

This installs `libketama` and its header, `ketama.h`.

## Usage (C)

```c
#include <ketama.h>
#include <stdio.h>

int main(void) {
    ketama_continuum c;

    if (!ketama_roll(&c, "ketama.servers")) {
        fprintf(stderr, "error: %s\n", ketama_error());
        return 1;
    }

    mcs *server = ketama_get_server("user:1234", c);
    printf("user:1234 -> %s\n", server->ip);

    ketama_smoke(c);
    return 0;
}
```

`ketama_roll` loads the server file and builds the continuum. `ketama_get_server` returns the server for a key. `ketama_smoke` releases the continuum when you are done.

## Language bindings

Bindings wrap the C library, or reimplement the same algorithm, so that every client maps keys identically. This lets services written in different languages share one cache pool without conflicts.

| Directory  | Language |
|------------|----------|
| `libketama` | C (core library) |
| `php_ketama` | PHP extension |
| `java_ketama` | Java |
| `python_ketama` | Python |
| `perl_ketama` | Perl |
| `erlang` | Erlang |

See the README in each directory for build steps and examples.

## Compatibility

Because the algorithm is fully specified (MD5, point count per weight, and server ordering), any correct implementation gives the same mapping for the same server file. When you write a new binding, test it against the C library with a shared server list and a large sample of keys.

## Contributing

Bug reports, fixes, and new bindings are welcome. Please include tests that check your mapping matches the reference C implementation.

## License

See the `LICENSE` file for details.

---

Note: I corrected "langauge" to "language" in the description. I haven't saved this to a file. Tell me if you want it written to `README.md` in your project directory, or if the API names and binding directories should match a specific codebase.
