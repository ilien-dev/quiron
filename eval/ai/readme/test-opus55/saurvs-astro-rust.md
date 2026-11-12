# astro-rust

**Astronomical algorithms in Rust**

`astro-rust` is a library of algorithms for positional astronomy, written in pure Rust. It computes the positions of the Sun, Moon, planets and stars, converts between coordinate systems, handles the many time scales astronomers use, and predicts events such as rise and set times, equinoxes, solstices, lunar phases and eclipses.

The library aims to be accurate, well-documented and dependency-light, so it can be used anywhere from a desktop planetarium to an embedded telescope controller.

---

## Features

- **Time and calendars**
  - Julian Day and Modified Julian Day conversions
  - Gregorian and Julian calendar support
  - Conversions between UT, TT, TAI and TDB
  - Delta T estimation for historical and future dates
  - Greenwich and local sidereal time (mean and apparent)

- **Coordinate systems**
  - Equatorial, ecliptic, horizontal and galactic coordinates
  - Precession, nutation and aberration corrections
  - Atmospheric refraction
  - Proper motion of stars

- **The Sun**
  - Geocentric position, apparent longitude and distance
  - Equation of time
  - Equinoxes and solstices

- **The Moon**
  - Geocentric position, distance and parallax
  - Phases, illuminated fraction and position angle of the bright limb
  - Perigee, apogee and node passages

- **Planets**
  - Heliocentric positions from VSOP87 series
  - Geocentric apparent positions with light-time correction
  - Elongation, phase angle and apparent magnitude
  - Conjunctions and oppositions

- **Events**
  - Rise, transit and set times for any body
  - Solar and lunar eclipses
  - Twilight (civil, nautical and astronomical)

- **Orbits**
  - Elliptic, parabolic and hyperbolic orbits
  - Kepler's equation solvers
  - Positions of comets and minor planets from orbital elements

---

## Installation

Add the crate to your `Cargo.toml`:

```toml
[dependencies]
astro = "2.0"
```

Or use Cargo directly:

```sh
cargo add astro
```

The library requires Rust 1.70 or newer.

---

## Quick start

### Julian Day

Almost every calculation begins with a Julian Day, a continuous count of days used to avoid the irregularities of calendars.

```rust
use astro::time::{self, CalType, Date};

fn main() {
    let date = Date {
        year: 2026,
        month: 11,
        decimal_day: 12.5,
        cal_type: CalType::Gregorian,
    };

    let jd = time::julian_day(&date);
    println!("Julian Day: {jd}");
}
```

### Position of the Sun

```rust
use astro::{sun, time};

fn main() {
    let jd = 2_461_357.0;

    let (ecl_point, distance_km) = sun::geocent_ecl_pos(jd);

    println!("Longitude: {:.4}°", ecl_point.long.to_degrees());
    println!("Latitude:  {:.4}°", ecl_point.lat.to_degrees());
    println!("Distance:  {:.0} km", distance_km);
}
```

### Position of a planet

```rust
use astro::planet::{self, Planet};

fn main() {
    let jd = 2_461_357.0;

    let (long, lat, rad_vec) = planet::heliocent_coords(&Planet::Mars, jd);

    println!("Mars heliocentric longitude: {:.4}°", long.to_degrees());
    println!("Mars heliocentric latitude:  {:.4}°", lat.to_degrees());
    println!("Distance from the Sun:       {:.6} AU", rad_vec);
}
```

### Equatorial to horizontal coordinates

```rust
use astro::{coords, angle};

fn main() {
    let hour_angle = angle::deg_frm_hms(3, 15, 0.0).to_radians();
    let declination = angle::deg_frm_dms(-6, 43, 0.0).to_radians();
    let observer_lat = 40.4168_f64.to_radians();

    let azimuth = coords::az_frm_eq(hour_angle, declination, observer_lat);
    let altitude = coords::alt_frm_eq(hour_angle, declination, observer_lat);

    println!("Azimuth:  {:.2}°", azimuth.to_degrees());
    println!("Altitude: {:.2}°", altitude.to_degrees());
}
```

---

## Conventions

To keep the API predictable, the library follows a few conventions throughout:

- **Angles are in radians.** Helper functions in the `angle` module convert to and from degrees, hours, and sexagesimal notation.
- **Distances** are in kilometres for the Moon and Sun, and in astronomical units for planets, unless a function's documentation says otherwise.
- **Time** is passed as a Julian Day (`f64`). Functions document whether they expect Universal Time (UT) or Terrestrial Time (TT); use `time::delta_t` to convert between them.
- **Longitudes** on Earth are measured positive *west* of Greenwich, following the convention in classical astronomical literature. Be careful when supplying coordinates from GPS or mapping services, which usually measure positive east.

---

## Accuracy

The algorithms are based on well-established methods from the astronomical literature, including Jean Meeus's *Astronomical Algorithms*, the VSOP87 planetary theory, and the ELP-2000/82 lunar theory.

Typical accuracy for dates within a few centuries of the present:

| Quantity | Typical error |
| --- | --- |
| Solar longitude | < 1 arcsecond |
| Lunar longitude | ~10 arcseconds |
| Planetary positions | < 1 arcsecond (inner planets) |
| Rise and set times | ~1 minute |
| Equinoxes and solstices | < 1 minute |

Accuracy degrades for dates far from the present, mainly because of uncertainty in Delta T. For research-grade work spanning millennia, or for spacecraft navigation, consider using JPL ephemerides directly.

---

## Documentation

Full API documentation is available on [docs.rs](https://docs.rs/astro). To build it locally:

```sh
cargo doc --open
```

Each function's documentation lists its inputs, outputs, units, and the source of the algorithm.

---

## Running the tests

```sh
cargo test
```

The test suite checks results against worked examples from the literature and values published in astronomical almanacs.

---

## Contributing

Contributions are welcome. Good places to start:

- Adding algorithms that aren't yet implemented
- Improving accuracy or performance of existing routines
- Expanding tests with known reference values
- Improving documentation and examples

Before opening a pull request:

1. Run `cargo fmt` and `cargo clippy` and resolve any warnings.
2. Add tests for new functionality, ideally against a published reference value.
3. Cite the source of any algorithm in its documentation comment.

Please open an issue first for large changes so the approach can be discussed.

---

## References

- Meeus, J. *Astronomical Algorithms*, 2nd ed. Willmann-Bell, 1998.
- Bretagnon, P. & Francou, G. "Planetary theories in rectangular and spherical variables: VSOP87 solutions." *Astronomy and Astrophysics*, 202, 1988.
- Chapront-Touzé, M. & Chapront, J. *Lunar Tables and Programs from 4000 B.C. to A.D. 8000*. Willmann-Bell, 1991.
- *The Astronomical Almanac*. U.S. Naval Observatory and HM Nautical Almanac Office.

---

## License

This project is licensed under the MIT License. See [LICENSE](LICENSE) for details.
