import colorsys
import math
import re
import os

# --- Base TOML Theme Template ---
# (The large TOML structure provided previously, with the [palette] section
# replaced by a placeholder)

TOML_TEMPLATE = """
"attribute" = "C9"
"comment" = { fg = "C3" }
"constant" = "C7"
"constant.builtin" = { fg = "C7", modifiers = ["italic"] }
"constant.character" = "C9"
"constant.character.escape" = { fg = "C9", modifiers = ["bold"] }
"constant.numeric" = "C7"
"constructor" = "C9"
"function" = { fg = "C9", modifiers = ["bold"] }
"function.builtin" = { fg = "C5", modifiers = ["bold", "italic"] }
"function.macro" = "C5"
"function.special" = "C5"
"keyword" = { fg = "C5", modifiers = ["italic"] }
"keyword.control" = { fg = "C9", modifiers = ["bold", "italic"] }
"keyword.control.conditional" = { fg = "C9", modifiers = ["bold", "italic"] }
"keyword.control.exception" = { fg = "C5", modifiers = ["bold", "italic"] }
"keyword.control.import" = { fg = "C5", modifiers = ["italic"] }
"keyword.control.repeat" = { fg = "C9", modifiers = ["bold", "italic"] }
"keyword.control.return" = { fg = "C9", modifiers = ["bold", "italic"] }
"keyword.directive" = { fg = "C5", modifiers = ["italic"] }
"keyword.function" = { fg = "C5", modifiers = ["italic"] }
"keyword.operator" = { fg = "C5", modifiers = ["bold"] }
"keyword.storage" = { fg = "C5", modifiers = ["italic"] }
"keyword.type" = { fg = "C5", modifiers = ["italic"] }
"label" = "C9"
"namespace" = { fg = "C4" }
"operator" = "C7"
"punctuation" = "C5"
"punctuation.delimiter" = "C5"
"punctuation.bracket" = "C5"
"string" = "C5"
"string.regexp" = "C5"
"tag" = "C9"
"type" = { fg = "C5" }
"type.builtin" = { fg = "C5", modifiers = ["italic"] }
"variable" = "C7"
"variable.builtin" = { fg = "C5", modifiers = ["italic"] }
"variable.other.member" = "C9"
"variable.parameter" = "C7"

"special" = "highlight"
"markup.bold" = { modifiers = ["bold"] }
"markup.heading" = { fg = "C9", modifiers = ["bold"] }
"markup.italic" = { modifiers = ["italic"] }
"markup.link.text" = { modifiers = ["italic"] }
"markup.link.url" = { fg = "C9", modifiers = ["underlined"] }
"markup.list" = "C9"
"markup.raw" = "C9"
"markup.strikethrough" = { modifiers = ["crossed_out"] }

"ui.background" = { fg = "C3", bg = "C0" }
"ui.cursor.match" = { fg = "C0", bg = "highlight", modifiers = ["bold"] }
"ui.cursor.primary" = { fg = "C9", bg = "highlight2" }
"ui.cursorline" = { bg = "C2" }
"ui.debug.breakpoint" = { fg = "C5" }
"ui.debug.active" = { fg = "C9" }
"ui.gutter" = { bg = "C0" }
"ui.linenr" = { fg = "C1" }
"ui.linenr.selected" = { fg = "C2", modifiers = ["bold"] }
"ui.popup" = { fg = "C5", bg = "C0" }
"ui.menu" = { fg = "C5", bg = "C0" }
"ui.menu.selected" = { fg = "C5", bg = "C3" }
"ui.help" = { fg = "C5", bg = "C0" }
"ui.selection" = { fg = "C9", bg = "highlight" }
"ui.selection.primary" = { fg = "C9", bg = "highlight2" }
"ui.statusline" = { fg = "C5", bg = "C0" }
"ui.statusline.inactive" = { fg = "C3", bg = "C0" }
"ui.statusline.normal" = { fg = "C3", bg = "C0", modifiers = ["bold"] }
"ui.statusline.insert" = { fg = "C3", bg = "C0", modifiers = ["bold"] }
"ui.statusline.select" = { fg = "C3", bg = "C0", modifiers = ["bold"] }
"ui.text" = { fg = "C5" }
"ui.text.focus" = { fg = "C9", bg = "C3", modifiers = ["bold"] }
"ui.virtual.indent-guide" = "C1"
"ui.virtual.ruler" = { bg = "C2" }
"ui.virtual.whitespace" = "C3"
"ui.window" = { fg = "C5" }

"diagnostic.error" = { underline = { color = "C9", style = "curl" } }
"diagnostic.warning" = { underline = { color = "C5", style = "dashed" } }
"diagnostic.info" = { underline = { color = "C5", style = "dotted" } }
"diagnostic.hint" = { underline = { color = "C5", style = "dotted" } }
"diagnostic.unnecessary" = { modifiers = ["dim"] }
"diagnostic.deprecated" = { modifiers = ["crossed_out"] }

"diff.plus" = { fg = "C4", modifiers = ["bold"] }
"diff.delta" = { fg = "C3", modifiers = ["italic"] }
"diff.minus" = { fg = "C2", modifiers = ["crossed_out"] }

##PALETTE_PLACEHOLDER##
"""

# --- Helper Functions ---

def lerp(a, b, t):
  """Linearly interpolates between a and b by t (clamped)."""
  t = max(0.0, min(1.0, t))
  return a + (b - a) * t

def lerp_hue(h1, h2, t):
  """Linearly interpolates between two hues (0-1 range), handling wrapping."""
  t = max(0.0, min(1.0, t))
  diff = h2 - h1
  if abs(diff) > 0.5:
    if diff > 0:
      h1 += 1.0
    else:
      h2 += 1.0
    diff = h2 - h1
  interpolated_hue = h1 + diff * t
  return interpolated_hue % 1.0

def hsl_to_hex(h, s, l, gamma = 1):
  """Converts HSL (0-1 range) to a hex color string."""
  h = max(0.0, min(1.0, h))
  s = max(0.0, min(1.0, s))
  l = max(0.0, min(1.0, l))
  r, g, b = colorsys.hls_to_rgb(h, l, s)
  r = pow(r, gamma)
  g = pow(g, gamma)
  b = pow(b, gamma)
  r = int(max(0, min(255, r * 255)))
  g = int(max(0, min(255, g * 255)))
  b = int(max(0, min(255, b * 255)))
  return f"#{r:02x}{g:02x}{b:02x}"

# --- Palette Generation Function ---

def generate_linear_palette(
    name,
    light_hue_deg,
    mid_hue_deg,
    dark_hue_deg,
    white_brightness=0.95, # Corresponds to C<N-1>
    dark_brightness=0.05,  # Corresponds to C0
    min_saturation=0.1,
    max_saturation=0.6,
    num_colors=10,
    highlight_saturation_scale=0.7,
    highlight_lightness=0.5,
    gamma_correction=0.5 # Gamma correction factor, default for dark themes
):
  """
  Generates a palette dictionary C0..C<N-1>, highlight, highlight2.
  (Args documentation omitted for brevity)
  Returns:
    A dictionary containing the palette colors.
  """
  if num_colors < 2:
      raise ValueError("num_colors must be at least 2")

  h_light = light_hue_deg / 360.0
  h_mid = mid_hue_deg / 360.0
  h_dark = dark_hue_deg / 360.0

  palette = {"name": name} # Keep name internally

  for i in range(num_colors):
    t = i / (num_colors - 1)
    # Interpolate lightness between dark_brightness (C0) and white_brightness (C<N-1>)
    l = lerp(dark_brightness, white_brightness, t)
    # Saturation peaks in the middle of the range
    peak_factor = 1.0 - 2.0 * abs(t - 0.5)
    s = lerp(min_saturation, max_saturation, peak_factor)

    # Interpolate hue in two stages: light->mid and mid->dark
    if t <= 0.5:
      hue_t = t * 2.0
      h = lerp_hue(h_light, h_mid, hue_t)
    else:
      hue_t = (t - 0.5) * 2.0
      h = lerp_hue(h_mid, h_dark, hue_t)

    # Apply gamma correction during HSL to Hex conversion
    palette[f"C{i}"] = hsl_to_hex(h, s, l, gamma=gamma_correction)

  # Generate highlight colors (using the original gamma correction for consistency)
  palette["highlight"] = hsl_to_hex(
      h_mid,
      highlight_saturation_scale,
      highlight_lightness,
      gamma=1
  )
  palette["highlight2"] = hsl_to_hex(
      lerp_hue(h_dark, (dark_hue_deg + 20) / 360.0, 0.5),
      highlight_saturation_scale * 0.8,
      highlight_lightness * 0.9,
      gamma=1
  )
  return palette

# --- Formatting and File Functions ---

def sanitize_filename(name):
    """Converts a palette name into a safe filename component."""
    name = name.lower()
    name = re.sub(r'\s+', '_', name)
    name = re.sub(r'[()]', '', name)
    name = re.sub(r'[^a-z0-9_]+', '', name)
    return name

def format_palette_section(palette):
  """Formats just the palette key-value pairs for TOML insertion."""
  lines = ["[palette]"] # Start with the section header
  # Sort C0, C1, ... CN-1 numerically
  color_keys = sorted([k for k in palette if k.startswith("C")], key=lambda x: int(x[1:]))
  # Sort highlight, highlight2 alphabetically
  highlight_keys = sorted([k for k in palette if k.startswith("highlight")])

  for key in color_keys + highlight_keys:
      lines.append(f'{key} = "{palette[key]}"')
  return "\n".join(lines)

# --- Define Palette Parameters ---

# Note: white_brightness corresponds to C9, dark_brightness to C0 in a 10-color palette

# Sunset Palette (Dark)
sunset_params = {
    "name": "Sunset",
    "light_hue_deg": 220, # Hue for C9 (brightest)
    "mid_hue_deg": 30,    # Hue around C4/C5
    "dark_hue_deg": 280,  # Hue for C0 (darkest)
    "white_brightness": 1.0, # Lightness of C9
    "dark_brightness": 0.02, # Lightness of C0
    "min_saturation": 0.10,
    "max_saturation": 0.30,
    "highlight_saturation_scale": 0.6,
    "highlight_lightness": 0.55,
    "gamma_correction": 0.5 # Gamma correction for dark bg
}

# Tech Sunset Palette (Dark)
tech_sunset_params = {
    "name": "Tech Sunset",
    "light_hue_deg": 180,
    "mid_hue_deg": 120,
    "dark_hue_deg": 60,
    "white_brightness": 1.0,
    "dark_brightness": 0.02,
    "min_saturation": 0.05,
    "max_saturation": 0.55,
    "highlight_saturation_scale": 0.7,
    "highlight_lightness": 0.5,
    "gamma_correction": 0.5
}

# Forest Sunset Palette (Dark)
forest_sunset_params = {
    "name": "Forest Sunset",
    "light_hue_deg": 40,
    "mid_hue_deg": 100,
    "dark_hue_deg": 25,
    "white_brightness": 1.0,
    "dark_brightness": 0.02,
    "min_saturation": 0.08,
    "max_saturation": 0.30,
    "highlight_saturation_scale": 0.5,
    "highlight_lightness": 0.45,
    "gamma_correction": 0.5
}

# Cyberpunk Matrix Palette (Dark)
cyberpunk_params = {
    "name": "Cyberpunk Matrix",
    "light_hue_deg": 210,
    "mid_hue_deg": 275,
    "dark_hue_deg": 185,
    "white_brightness": 1.0,
    "dark_brightness": 0.02,
    "min_saturation": 0.15,
    "max_saturation": 0.65,
    "highlight_saturation_scale": 0.8,
    "highlight_lightness": 0.55,
    "gamma_correction": 0.5
}

# --- Generate and Save Full Theme Files ---

dark_palettes_params = [
    sunset_params,
    forest_sunset_params,
    tech_sunset_params,
    cyberpunk_params
]

# --- Generate Light Mode Variants ---
light_palettes_params = []
for params in dark_palettes_params:
    light_params = params.copy() # Create a copy to modify

    # --- Resolve TODO: swap the white_brightness and dark_brightness ---
    # For light themes, C0 should be light and C9 should be dark.
    original_white_brightness = params['white_brightness']
    original_dark_brightness = params['dark_brightness']
    light_params['white_brightness'] = original_dark_brightness # C9 is now dark
    light_params['dark_brightness'] = original_white_brightness # C0 is now light
    # --- End Resolve TODO ---

    # Adjust name
    light_params['name'] = params['name'] + " Light"

    # Adjust gamma correction for light backgrounds
    light_params['gamma_correction'] = 0.7
    light_params['max_saturation'] = min(1, light_params['max_saturation'] * 1.5)

    # Example: Slightly desaturate and brighten highlights for better contrast on black font
    light_params['highlight_lightness'] = min(1, params['highlight_lightness'] * 2) # Make highlights brighter

    light_palettes_params.append(light_params)

# Combine dark and light theme parameters into one list
all_palettes_params = dark_palettes_params + light_palettes_params

# Optional: Create the output directory if it doesn't exist
output_dir = "." # Save in the current directory
# if not os.path.exists(output_dir):
#     os.makedirs(output_dir)

print("Generating theme files...")

# Iterate over ALL parameter sets (dark and light)
for params in all_palettes_params:
  # Generate the color data using the specific parameters for this theme
  generated_palette = generate_linear_palette(**params)

  # Create a clean filename based on the theme's name
  base_filename = sanitize_filename(params['name'])
  output_filename = f"deep_focus_{base_filename}.toml"
  output_path = os.path.join(output_dir, output_filename)

  # Format the [palette] section string
  palette_toml_string = format_palette_section(generated_palette)

  # Replace the placeholder in the template with the generated palette
  full_toml_content = TOML_TEMPLATE.replace("##PALETTE_PLACEHOLDER##", palette_toml_string)
  # Remove leading/trailing whitespace that might result from template formatting
  full_toml_content = full_toml_content.strip()

  # Write the complete TOML content to the file
  try:
    with open(output_path, 'w') as f:
      f.write(full_toml_content)
    print(f"Successfully saved: {output_path}")
  except IOError as e:
    print(f"Error writing file {output_path}: {e}")

print("Finished.")
