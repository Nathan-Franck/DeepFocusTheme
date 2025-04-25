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
"ui.cursorline" = { bg = "C1" }
"ui.debug.breakpoint" = { fg = "C5" }
"ui.debug.active" = { fg = "C9" }
"ui.gutter" = { bg = "C0" }
"ui.linenr" = { fg = "C2" }
"ui.linenr.selected" = { fg = "C4", modifiers = ["bold"] }
"ui.popup" = { fg = "C7", bg = "C1" }
"ui.menu" = { fg = "C7", bg = "C1" }
"ui.menu.selected" = { fg = "C9", bg = "C3" }
"ui.help" = { fg = "C7", bg = "C1" }
"ui.selection" = { fg = "C9", bg = "highlight" }
"ui.selection.primary" = { fg = "C9", bg = "highlight2" }
"ui.statusline" = { fg = "C7", bg = "C1" }
"ui.statusline.inactive" = { fg = "C4", bg = "C0" }
"ui.statusline.normal" = { fg = "C9", bg = "C2", modifiers = ["bold"] }
"ui.statusline.insert" = { fg = "C9", bg = "C2", modifiers = ["bold"] }
"ui.statusline.select" = { fg = "C9", bg = "C2", modifiers = ["bold"] }
"ui.text" = { fg = "C7" }
"ui.text.focus" = { fg = "C9", bg = "C3", modifiers = ["bold"] }
"ui.virtual.indent-guide" = "C2"
"ui.virtual.ruler" = { bg = "C1" }
"ui.virtual.whitespace" = "C3"
"ui.window" = { fg = "C5" }

"diagnostic.error" = { underline = { color = "C9", style = "curl" } }
"diagnostic.warning" = { underline = { color = "C5", style = "dashed" } }
"diagnostic.info" = { underline = { color = "C5", style = "dotted" } }
"diagnostic.hint" = { underline = { color = "C5", style = "dotted" } }
"diagnostic.unnecessary" = { modifiers = ["dim"] }
"diagnostic.deprecated" = { modifiers = ["crossed_out"] }

"diff.plus" = { fg = "C9", modifiers = ["bold"] }
"diff.delta" = { fg = "C9", modifiers = ["italic"] }
"diff.minus" = { fg = "C9", modifiers = ["crossed_out"] }

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

def hsl_to_hex(h, s, l):
  """Converts HSL (0-1 range) to a hex color string."""
  h = max(0.0, min(1.0, h))
  s = max(0.0, min(1.0, s))
  l = max(0.0, min(1.0, l))
  r, g, b = colorsys.hls_to_rgb(h, l, s)
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
    white_brightness=0.95,
    dark_brightness=0.05,
    min_saturation=0.1,
    max_saturation=0.6,
    num_colors=10,
    highlight_saturation_scale=0.7,
    highlight_lightness=0.5
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
    l = lerp(dark_brightness, white_brightness, t)
    peak_factor = 1.0 - 2.0 * abs(t - 0.5)
    s = lerp(min_saturation, max_saturation, peak_factor)

    if t <= 0.5:
      hue_t = t * 2.0
      h = lerp_hue(h_light, h_mid, hue_t)
    else:
      hue_t = (t - 0.5) * 2.0
      h = lerp_hue(h_mid, h_dark, hue_t)

    palette[f"C{i}"] = hsl_to_hex(h, s, l)

  palette["highlight"] = hsl_to_hex(
      h_mid,
      highlight_saturation_scale,
      highlight_lightness
  )
  palette["highlight2"] = hsl_to_hex(
      lerp_hue(h_dark, (dark_hue_deg + 20) / 360.0, 0.5),
      highlight_saturation_scale * 0.8,
      highlight_lightness * 0.9
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
  color_keys = sorted([k for k in palette if k.startswith("C")], key=lambda x: int(x[1:]))
  highlight_keys = sorted([k for k in palette if k.startswith("highlight")])

  for key in color_keys + highlight_keys:
      lines.append(f'{key} = "{palette[key]}"')
  return "\n".join(lines)

# --- Define Palette Parameters ---

# Sunset Palette
sunset_params = {
    "name": "Sunset", # Simplified name for filename
    "light_hue_deg": 220,
    "mid_hue_deg": 30,
    "dark_hue_deg": 280,
    "white_brightness": 0.95,
    "dark_brightness": 0.05,
    "min_saturation": 0.10,
    "max_saturation": 0.30,
    "highlight_saturation_scale": 0.6,
    "highlight_lightness": 0.55
}

# Tech Sunset Palette
tech_sunset_params = {
    "name": "Tech Sunset",
    "light_hue_deg": 180,
    "mid_hue_deg": 120,
    "dark_hue_deg": 60,
    "white_brightness": 0.95,
    "dark_brightness": 0.05,
    "min_saturation": 0.05,
    "max_saturation": 0.55,
    "highlight_saturation_scale": 0.7,
    "highlight_lightness": 0.5
}

# Forest Sunset Palette
forest_sunset_params = {
    "name": "Forest Sunset",
    "light_hue_deg": 40,
    "mid_hue_deg": 100,
    "dark_hue_deg": 25,
    "white_brightness": 0.90,
    "dark_brightness": 0.05,
    "min_saturation": 0.08,
    "max_saturation": 0.30,
    "highlight_saturation_scale": 0.5,
    "highlight_lightness": 0.45
}

# Cyberpunk Matrix Palette
cyberpunk_params = {
    "name": "Cyberpunk Matrix",
    "light_hue_deg": 210,
    "mid_hue_deg": 275,
    "dark_hue_deg": 185,
    "white_brightness": 0.95,
    "dark_brightness": 0.06,
    "min_saturation": 0.15,
    "max_saturation": 0.65,
    "highlight_saturation_scale": 0.8,
    "highlight_lightness": 0.55
}

# --- Generate and Save Full Theme Files ---

palettes_to_generate = [
    sunset_params,
    forest_sunset_params,
    tech_sunset_params,
    cyberpunk_params
]

output_dir = "." # Save in the current directory
# Optional: Create the output directory if it doesn't exist
# if not os.path.exists(output_dir):
#     os.makedirs(output_dir)

print("Generating theme files...")

for params in palettes_to_generate:
  # Generate the color data
  generated_palette = generate_linear_palette(**params)

  # Create a clean filename
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
