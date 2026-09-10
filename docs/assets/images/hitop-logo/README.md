# HiTOP Logo Assets

Production asset family derived from the selected `Nested Strata` front mark.
The SVG files are the source of truth; raster assets must be regenerated from
them rather than edited independently.

## Masters

| File | Use |
| --- | --- |
| `hitop-logo-master-transparent.svg` | Canonical scalable master for transparent contexts |
| `hitop-logo-master-white.svg` | Canonical scalable master on white |
| `master/hitop-logo-master-transparent-2048.png` | High-resolution transparent raster master |
| `master/hitop-logo-master-white-2048.png` | High-resolution white-background raster master |

The four levels use `#1E3A5F`, `#264B7D`, `#3F7EB8`, and `#6AAFE0` from top
to bottom. Do not reorder, recolor, stretch, rotate, or add effects.

## Web and product assets

| Folder/file | Dimensions | Intended use |
| --- | ---: | --- |
| `web/hitop-logo-*-transparent.png` | 64–1024 px | Website, documentation, UI and presentations |
| `web/hitop-logo-*-white.png` | 64–1024 px | Same uses where a fixed white background is required |
| `webp/*.webp` | 256–1024 px | Lossless responsive web delivery |
| `favicon/favicon.ico` | 48 px | Legacy/browser favicon fallback |
| `favicon/favicon-{16,32,48}x*.png` | 16–48 px | Modern browser favicons |
| `favicon/apple-touch-icon-180.png` | 180 px | Apple touch icon |
| `favicon/pwa-icon-{192,512}.png` | 192/512 px | PWA icons |
| `favicon/pwa-maskable-512.png` | 512 px | Maskable PWA icon with safe padding |
| `platforms/github-avatar-500.png` | 500 px | GitHub organization/profile avatar |
| `platforms/github-avatar-500-transparent.png` | 500 px | Alternate transparent GitHub avatar |
| `platforms/social-avatar-400.png` | 400 px | Generic social/profile avatar |
| `platforms/slack-discord-512.png` | 512 px | Workspace/server avatar |
| `platforms/teams-color-192.png` | 192 px | Teams/Microsoft 365 full-color app icon; mark inside 120 px safe area |
| `platforms/teams-color-192-transparent.png` | 192 px | Optional transparent Teams color variant |
| `platforms/teams-outline-32.png` | 32 px | Teams/Microsoft 365 white outline icon |

## HTML integration

```html
<link rel="icon" href="/assets/images/hitop-logo/favicon/favicon.ico" sizes="any">
<link rel="icon" type="image/png" sizes="32x32" href="/assets/images/hitop-logo/favicon/favicon-32x32.png">
<link rel="icon" type="image/png" sizes="16x16" href="/assets/images/hitop-logo/favicon/favicon-16x16.png">
<link rel="apple-touch-icon" sizes="180x180" href="/assets/images/hitop-logo/favicon/apple-touch-icon-180.png">
<link rel="manifest" href="/assets/images/hitop-logo/site.webmanifest">
```

Teams assets follow Microsoft's 192 x 192 color-icon and 32 x 32 outline-icon
requirements. GitHub's 500 x 500 recommendation is used for profile/avatar
quality while remaining below its 3000 x 3000 maximum.
