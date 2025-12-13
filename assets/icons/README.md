# Icons Directory

This directory contains icon files for the Floor Plan Drawing App toolbar and menu items.

## Required Icons (Minimum)

These icons are used in the main toolbar and should be provided for the best user experience:

### Tool Icons
1. **`select.png`** (or `.svg`, `.ico`)
   - **Purpose**: Selection/pointer tool
   - **Recommended**: Cursor/pointer icon
   - **Resolution**: 24x24 pixels (minimum), 48x48 pixels (recommended for high-DPI)
   - **File Types**: PNG (preferred), SVG, ICO

2. **`draw_room.png`** (or `.svg`, `.ico`)
   - **Purpose**: Draw room tool
   - **Recommended**: Rectangle/square icon
   - **Resolution**: 24x24 pixels (minimum), 48x48 pixels (recommended for high-DPI)
   - **File Types**: PNG (preferred), SVG, ICO

3. **`draw_pathway.png`** (or `.svg`, `.ico`)
   - **Purpose**: Draw pathway tool
   - **Recommended**: Line/path icon
   - **Resolution**: 24x24 pixels (minimum), 48x48 pixels (recommended for high-DPI)
   - **File Types**: PNG (preferred), SVG, ICO

## Optional Icons (Enhanced UI)

These icons enhance the menu bar experience but are not required:

### File Menu Icons
4. **`open.png`** - Open Image action
5. **`new_floor.png`** - New Floor action
6. **`save.png`** - Save Project action
7. **`load.png`** - Load Project action

### View Menu Icons
8. **`zoom_in.png`** - Zoom In action
9. **`zoom_out.png`** - Zoom Out action
10. **`fit_window.png`** - Fit to Window action

## Icon Specifications

### File Format Priority
The application will try to load icons in this order:
1. PNG (`.png`) - **Recommended** for best compatibility
2. SVG (`.svg`) - Vector format, scales perfectly
3. ICO (`.ico`) - Windows icon format
4. JPG/JPEG (`.jpg`, `.jpeg`) - Not recommended but supported

### Resolution Guidelines
- **Minimum**: 24x24 pixels (for standard displays)
- **Recommended**: 48x48 pixels (for high-DPI/retina displays)
- **Maximum**: 256x256 pixels (for future scaling)

### Design Guidelines
- Use transparent backgrounds (PNG with alpha channel)
- Keep icons simple and recognizable
- Use consistent style across all icons
- Ensure icons are visible on both light and dark backgrounds
- Consider providing both light and dark variants if needed

## Icon Loading Behavior

The application will:
1. Look for icons in this directory (`assets/icons/`)
2. Try multiple file formats automatically
3. Fall back to text labels if icons are not found
4. Continue to function normally without icons

## Example Icon Sources

You can find free icons at:
- [Flaticon](https://www.flaticon.com/)
- [Icons8](https://icons8.com/)
- [Material Icons](https://fonts.google.com/icons)
- [Font Awesome](https://fontawesome.com/)

Make sure to check licensing requirements for any icons you use.
