---
name: Warm Editorial Memory
colors:
  surface: '#faf8ff'
  surface-dim: '#d2d9f4'
  surface-bright: '#faf8ff'
  surface-container-lowest: '#ffffff'
  surface-container-low: '#f2f3ff'
  surface-container: '#eaedff'
  surface-container-high: '#e2e7ff'
  surface-container-highest: '#dae2fd'
  on-surface: '#131b2e'
  on-surface-variant: '#3d4947'
  inverse-surface: '#283044'
  inverse-on-surface: '#eef0ff'
  outline: '#6d7a77'
  outline-variant: '#bcc9c6'
  surface-tint: '#006a61'
  primary: '#00685f'
  on-primary: '#ffffff'
  primary-container: '#008378'
  on-primary-container: '#f4fffc'
  inverse-primary: '#6bd8cb'
  secondary: '#515f74'
  on-secondary: '#ffffff'
  secondary-container: '#d5e3fc'
  on-secondary-container: '#57657a'
  tertiary: '#38645c'
  on-tertiary: '#ffffff'
  tertiary-container: '#517d75'
  on-tertiary-container: '#f4fffb'
  error: '#ba1a1a'
  on-error: '#ffffff'
  error-container: '#ffdad6'
  on-error-container: '#93000a'
  primary-fixed: '#89f5e7'
  primary-fixed-dim: '#6bd8cb'
  on-primary-fixed: '#00201d'
  on-primary-fixed-variant: '#005049'
  secondary-fixed: '#d5e3fc'
  secondary-fixed-dim: '#b9c7df'
  on-secondary-fixed: '#0d1c2e'
  on-secondary-fixed-variant: '#3a485b'
  tertiary-fixed: '#bdece2'
  tertiary-fixed-dim: '#a2d0c6'
  on-tertiary-fixed: '#00201c'
  on-tertiary-fixed-variant: '#224e47'
  background: '#faf8ff'
  on-background: '#131b2e'
  surface-variant: '#dae2fd'
typography:
  headline-xl:
    fontFamily: Plus Jakarta Sans
    fontSize: 36px
    fontWeight: '700'
    lineHeight: 44px
    letterSpacing: -0.02em
  headline-xl-mobile:
    fontFamily: Plus Jakarta Sans
    fontSize: 28px
    fontWeight: '700'
    lineHeight: 36px
    letterSpacing: -0.02em
  headline-lg:
    fontFamily: Plus Jakarta Sans
    fontSize: 28px
    fontWeight: '600'
    lineHeight: 36px
    letterSpacing: -0.015em
  headline-lg-mobile:
    fontFamily: Plus Jakarta Sans
    fontSize: 22px
    fontWeight: '600'
    lineHeight: 30px
    letterSpacing: -0.01em
  headline-md:
    fontFamily: Plus Jakarta Sans
    fontSize: 20px
    fontWeight: '600'
    lineHeight: 28px
    letterSpacing: -0.01em
  body-lg:
    fontFamily: Inter
    fontSize: 16px
    fontWeight: '400'
    lineHeight: 26px
  body-md:
    fontFamily: Inter
    fontSize: 14px
    fontWeight: '400'
    lineHeight: 22px
  label-lg:
    fontFamily: Inter
    fontSize: 15px
    fontWeight: '500'
    lineHeight: 20px
  label-md:
    fontFamily: Inter
    fontSize: 14px
    fontWeight: '500'
    lineHeight: 20px
  label-sm:
    fontFamily: Inter
    fontSize: 14px
    fontWeight: '600'
    lineHeight: 18px
rounded:
  sm: 0.25rem
  DEFAULT: 0.5rem
  md: 0.75rem
  lg: 1rem
  xl: 1.5rem
  full: 9999px
spacing:
  gutter: 1.5rem
  gutter-mobile: 0.75rem
  margin: 2.5rem
  margin-mobile: 1rem
  space-xs: 0.375rem
  space-sm: 0.5rem
  space-md: 1rem
  space-lg: 1.5rem
  space-xl: 2.5rem
---

## Brand & Style

The design system embodies a calm, warm, photographic sanctuary. Designed to reduce the anxiety of searching through decades of visual noise, it helps users surface half-remembered moments—sensory cues, fuzzy timeframes, partial scenery—without feeling like a sterile search engine. The emotional tone is nostalgic, respectful, patient, and quiet.

Visually, the style combines modern editorial minimalism with subtle warmth:
- Pure photo-forward hierarchy: UI chrome steps back to let imagery dominate.
- Tactile, crisp card surfaces that mimic physical photographic mounts.
- Atmospheric warmth through an unbleached paper backdrop (`#FAF9F5`) balanced against deep ink typography.
- Grounded, reassuring clarity: no flashy neon flourishes, but deliberate deep teal accents representing quiet discovery and intelligence.

## Colors

The palette is tuned around a gallery-like, warm daylight atmosphere:

- **Canvas & Backgrounds**: The foundational canvas uses `#FAF9F5` (warm linen/off-white), avoiding cold digital whites. Content surfaces and cards rest on `#FFFFFF` to produce gentle, natural contrast without harsh drop shadows.
- **Ink & Typography**: Deep midnight slate (`#0F172A`) commands high-clarity headlines and prominent numbers. Subdued descriptions, timestamps, and metadata live in slate (`#475569`), preserving soft visual hierarchy. Hairlines and component borders use crisp neutral slate (`#E2E8F0`).
- **Primary & Interactive**: Teal (`#0D9488`) drives actions, focused states, and identified memory matches. Soft teal washes (`#F0FDFA` and `#CCFBF1`) serve as interactive card selections, tag backgrounds, and hover fills.
- **Utility & Notice**: The top disclaimer banner is anchored in subtle neutral slate tint (`#F1F5F9`) with muted text (`#64748B`), keeping it legible yet secondary to library content.

## Typography

Typography balances welcoming, sculpted geometry with strict utilitarian readability:
- **Headings**: Set in **Plus Jakarta Sans** for soft terminals, warm humanist curves, and reassuring editorial presence. Headlines use tighter letter-spacing (`-0.01em` to `-0.02em`) for cohesion.
- **Body & Labels**: Built strictly in **Inter** to ensure maximum legibility when scanning metadata, camera details, timestamps, and confidence scores.
- **Accessibility Floor**: Minimum font size across all interfaces—including chips, badge counts, and legal disclaimers—is hard-locked to **14px** to guarantee effortless scanning for users of all ages.

## Layout & Spacing

The layout is structured around an adaptive 12-column responsive grid built for variable aspect-ratio photography and dense metadata inspection:

- **Desktop (>= 1024px)**: 12-column grid, `2.5rem` margins, `1.5rem` gutters. Photo memory results use dynamic 3- or 4-column cards with generous internal padding.
- **Tablet (768px - 1023px)**: 8-column grid, `2rem` margins, `1rem` gutters. Search prompts and facet filters collapse into a sticky horizontal scroll track.
- **Mobile (< 768px)**: 4-column grid, `1rem` margins, `0.75rem` gutters. Photo grids collapse to 1 or 2 columns, stacking conversational search queries directly above discovery carousels.

Generous whitespace between content clusters mirrors print photo albums, preventing visual exhaustion during open-ended browsing.

## Elevation & Depth

This system intentionally relies on **crisp structural layering and light-tint containment** rather than muddy drop shadows, ensuring UI elements never compete with photographic depth:

- **Layer 0 (Base)**: Warm paper foundation (`#FAF9F5`).
- **Layer 1 (Card & Mounts)**: Solid white (`#FFFFFF`) with a clean `1px solid #E2E8F0` border. A micro ambient shadow (`0 1px 2px 0 rgba(15, 23, 42, 0.04)`) provides subtle separation without creating artificial darkness.
- **Layer 2 (Floating & Active Modals)**: Active inspection overlays and floating search bars use white surfaces with a crisp border (`#E2E8F0`) reinforced by a soft diffused wash (`0 12px 24px -4px rgba(15, 23, 42, 0.08)`).
- **Selection States**: Active cards and chips exchange the neutral border for a precise teal stroke (`#0D9488`) backed by a soft tint glow (`#F0FDFA`), signaling selection through tone rather than dramatic lift.

## Shapes

The interface balances soft friendliness with structured precision:
- **Cards & Media Panels**: Set to `rounded-xl` (`12px` / `0.75rem`), rounding the photograph corners slightly to produce a warm, handheld print sensation without cutting into edge composition.
- **Interactive Buttons & Form Fields**: Standardized to `8px` (`0.5rem`) for a clean, sturdy feel.
- **Chips, Badges, and Filter Pills**: Pill-shaped (`9999px` fully rounded) to reinforce tactile filter manipulation and tactile clickability.

## Components

### Demo Disclaimer Banner
- Anchored at the very top of the viewport.
- Flat background in `#F1F5F9` with a subtle 1px bottom border in `#E2E8F0`.
- Text: `14px`, Inter medium, `#64748B`.
- Content: `"Demo library · AI-generated and stock images · not your real photos"`, centered with a subtle lock or info icon.

### Cards & Photo Items
- Background: `#FFFFFF`.
- Border: `1px solid #E2E8F0`.
- Radius: `12px` (`rounded-xl`).
- Photo presentation: Edge-to-edge top display with a `12px 12px 0 0` crop or framed with an interior 8px white mount.
- Hover state: Border shifts to `#CBD5E1`; subtle image zoom (scale `1.02`).
- Selected state: Border shifts to `2px solid #0D9488` with `#F0FDFA` bottom panel tint.

### Memory Filter Chips & Pills
- Default state: `#FFFFFF` pill, `1px solid #E2E8F0`, slate text (`#475569`), min height 36px, `14px` font size. Contains counter badge (e.g., `"Dog in snow · 14"`).
- Selected state: Teal fill tint (`#F0FDFA`), `1.5px solid #0D9488`, teal label text (`#0F766E`), prefixed with an accessible bold checkmark: `"✓ Dog in snow · 14"`.
- Focus state: `2px solid #0D9488` ring with `2px` offset.

### Search & Recall Query Input
- Conversational, warm query input styled like a natural language sketchbook.
- Background `#FFFFFF`, `1px solid #E2E8F0`, inner padding `14px 18px`, text `16px` Inter.
- Placeholder copy: `"Describe what you remember (e.g., yellow raincoat in Lisbon, rainy afternoon)..."` in `#94A3B8`.
- Focus: Ring of `2px solid #0D9488` with smooth opacity transition.

### Buttons
- **Primary**: Deep teal `#0D9488` background, `#FFFFFF` text, `8px` radius, `14px` Inter SemiBold, padding `10px 20px`. Hover: `#0F766E`.
- **Secondary / Ghost**: Pure white `#FFFFFF` surface, `1px solid #E2E8F0`, text `#0F172A`. Hover: `#F8FAFC`.
- **Active / Filter Button**: Pill-shaped with soft teal background `#CCFBF1` and `#0F766E` text.

### Form Inputs & Checkboxes
- **Checkboxes**: `18px x 18px`, `4px` rounded corners. Default border `#CBD5E1`. Checked state: filled `#0D9488` with a crisp white centered checkmark (`✓`).
- **Radio Buttons**: `18px x 18px` circular control, `#0D9488` ring and centered teal dot when selected.

### Memory Cue Drawer / Inspector
- Slide-over card for inspecting photo clues (extracted objects, approximate year, seasonal weather matches, camera metadata).
- Surface `#FFFFFF`, separated by a `1px` border `#E2E8F0`, structured with spacious 16px vertical blocks and clear 14px badges.