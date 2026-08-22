---
name: GlobeTrotter
colors:
  surface: '#f8f9fa'
  surface-dim: '#d9dadb'
  surface-bright: '#f8f9fa'
  surface-container-lowest: '#ffffff'
  surface-container-low: '#f3f4f5'
  surface-container: '#edeeef'
  surface-container-high: '#e7e8e9'
  surface-container-highest: '#e1e3e4'
  on-surface: '#191c1d'
  on-surface-variant: '#43474f'
  inverse-surface: '#2e3132'
  inverse-on-surface: '#f0f1f2'
  outline: '#737780'
  outline-variant: '#c3c6d1'
  surface-tint: '#3a5f94'
  primary: '#001e40'
  on-primary: '#ffffff'
  primary-container: '#003366'
  on-primary-container: '#799dd6'
  inverse-primary: '#a7c8ff'
  secondary: '#a43c12'
  on-secondary: '#ffffff'
  secondary-container: '#fe7e4f'
  on-secondary-container: '#6b1f00'
  tertiary: '#112121'
  on-tertiary: '#ffffff'
  tertiary-container: '#263636'
  on-tertiary-container: '#8e9f9e'
  error: '#ba1a1a'
  on-error: '#ffffff'
  error-container: '#ffdad6'
  on-error-container: '#93000a'
  primary-fixed: '#d5e3ff'
  primary-fixed-dim: '#a7c8ff'
  on-primary-fixed: '#001b3c'
  on-primary-fixed-variant: '#1f477b'
  secondary-fixed: '#ffdbcf'
  secondary-fixed-dim: '#ffb59c'
  on-secondary-fixed: '#380c00'
  on-secondary-fixed-variant: '#822800'
  tertiary-fixed: '#d4e6e5'
  tertiary-fixed-dim: '#b8cac9'
  on-tertiary-fixed: '#0e1e1e'
  on-tertiary-fixed-variant: '#3a4a49'
  background: '#f8f9fa'
  on-background: '#191c1d'
  surface-variant: '#e1e3e4'
  deep-ocean: '#001F3F'
  sunset-accent: '#FF4500'
  slate-gray: '#333333'
  cloud-white: '#FFFFFF'
typography:
  display-lg:
    fontFamily: ebGaramond
    fontSize: 64px
    fontWeight: '600'
    lineHeight: '1.1'
    letterSpacing: -0.02em
  headline-lg:
    fontFamily: ebGaramond
    fontSize: 48px
    fontWeight: '500'
    lineHeight: '1.2'
  headline-lg-mobile:
    fontFamily: ebGaramond
    fontSize: 32px
    fontWeight: '500'
    lineHeight: '1.2'
  headline-md:
    fontFamily: ebGaramond
    fontSize: 32px
    fontWeight: '500'
    lineHeight: '1.3'
  title-lg:
    fontFamily: hankenGrotesk
    fontSize: 22px
    fontWeight: '600'
    lineHeight: 28px
  body-lg:
    fontFamily: hankenGrotesk
    fontSize: 18px
    fontWeight: '400'
    lineHeight: 28px
  body-md:
    fontFamily: hankenGrotesk
    fontSize: 16px
    fontWeight: '400'
    lineHeight: 24px
  label-md:
    fontFamily: hankenGrotesk
    fontSize: 14px
    fontWeight: '600'
    lineHeight: 20px
    letterSpacing: 0.05em
  label-sm:
    fontFamily: hankenGrotesk
    fontSize: 12px
    fontWeight: '500'
    lineHeight: 16px
    letterSpacing: 0.03em
rounded:
  sm: 0.25rem
  DEFAULT: 0.5rem
  md: 0.75rem
  lg: 1rem
  xl: 1.5rem
  full: 9999px
spacing:
  container-max: 1280px
  gutter: 24px
  margin-desktop: 64px
  margin-mobile: 20px
  unit-xs: 4px
  unit-sm: 8px
  unit-md: 16px
  unit-lg: 32px
  unit-xl: 64px
---

## Brand & Style
The design system embodies a **Premium Travel Startup** aesthetic, positioning itself at the intersection of luxury heritage and modern digital efficiency. It is designed to evoke a sense of organized adventure—reliable enough for logistics, yet evocative enough to inspire wanderlust.

The visual direction is **Modern / Minimalist** with a focus on **High-Contrast Bold** elements. It utilizes generous whitespace to create an "airy" feel, allowing high-quality destination photography to serve as the primary emotional driver. The style leverages sophisticated layering and large-scale typography to establish a clear information hierarchy that feels both curated and professional.

## Colors
The palette is anchored by **Deep Oceanic Blues** (`primary`) to establish trust and depth, contrasted by **Sunset Orange** (`secondary`) for high-priority calls to action and navigational highlights. 

- **Primary:** Used for brand presence, navigation backgrounds, and primary headings.
- **Secondary:** Used sparingly for "Book Now" buttons, active states, and critical accent points.
- **Tertiary:** A soft, desaturated teal used for subtle background sections and secondary containers.
- **Neutrals:** A range of whites and light grays form the canvas, ensuring the interface remains legible and "airy."

The system defaults to **Light Mode** to maintain a fresh, travel-journal feel, utilizing high-contrast text (`slate-gray`) for maximum readability.

## Typography
The typographic strategy uses a dual-font system to balance luxury and utility. 

**Headings** utilize **EB Garamond**, a classical serif that brings a sense of "heritage travel" and premium editorial quality. Use this for page titles, section headers, and promotional display text.

**UI & Body** text utilizes **Hanken Grotesk**, a sharp, contemporary sans-serif. This font provides the "modern efficiency" required for complex itinerary planning, ensuring that dense travel data (times, prices, coordinates) remains highly legible and professional.

For mobile layouts, `headline-lg` should scale down to `32px` to prevent awkward wrapping while maintaining its elegant character.

## Layout & Spacing
The layout follows a **Fluid Grid** model with a maximum content width of 1280px to ensure a premium, centered viewing experience on large monitors. 

- **Desktop:** 12-column grid with 24px gutters and 64px side margins. 
- **Tablet:** 8-column grid with 20px gutters and 40px margins.
- **Mobile:** 4-column grid with 16px gutters and 20px margins.

Spacing is governed by an 8px base unit. Use `unit-xl` for section separation to maintain "generous whitespace," while `unit-md` is the default for internal component padding. Group related content closely using `unit-sm` to maintain a clear visual relationship.

## Elevation & Depth
Depth is created through **Tonal Layers** and **Ambient Shadows** rather than heavy gradients. 

- **Surface Levels:** The primary background is `cloud-white`. Elevated elements like cards and modal dialogs use `cloud-white` but are distinguished by a "soft-depth" shadow: 0px 4px 20px rgba(0, 0, 0, 0.05).
- **Glassmorphism:** Navigation bars and image overlays should use a subtle backdrop blur (12px) with a 70% opacity white fill to maintain context of the background imagery while ensuring text legibility.
- **Interaction:** Upon hover, interactive cards should slightly lift—increasing shadow spread and decreasing opacity—to provide tactile feedback without breaking the minimalist aesthetic.

## Shapes
In alignment with the "2xl" requirement, the design system utilizes a **Rounded** shape language. 

- **Standard Components:** Buttons, input fields, and small tags use a `0.5rem` (8px) radius.
- **Large Components:** Cards, image containers, and main content modules use `rounded-xl` (24px) to create a soft, inviting, and modern look.
- **Avatars:** Strictly circular to distinguish human elements from functional UI.

All image containers must have a slight inner stroke (1px, 5% black) to ensure they don't bleed into the white background if the image is very light.

## Components

### Buttons
- **Primary:** Solid `primary_color_hex` with white `label-md` text. High roundedness.
- **Secondary/CTA:** Solid `secondary_color_hex`. Used for final conversion points (e.g., "Confirm Booking").
- **Ghost:** `primary_color_hex` border (1px) with transparent background for low-priority actions.

### Cards
Cards are the primary vehicle for itinerary items and destinations. They must feature a high-aspect-ratio image at the top with `rounded-xl` corners. Information should be layered over the image using a semi-transparent glassmorphic tag in the top-right corner for metadata like "Price" or "Rating."

### Input Fields
Inputs should be clean with a 1px border of `tertiary_color_hex`. On focus, the border transitions to `primary_color_hex`. Use `body-md` for user input and `label-sm` for floating labels above the field.

### Chips & Tags
Use for activity categories (e.g., "Sightseeing", "Food"). These should have a background of `tertiary_color_hex` and `primary_color_hex` text, using the `label-sm` style.

### Itinerary Lists
Vertical timelines using a thin 2px dashed line in `tertiary_color_hex` to connect stops. Each stop is a mini-card with an icon representing the activity type.