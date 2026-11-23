import os
import random
import numpy as np

def generate_runs(dither_arr):
    h, w = dither_arr.shape
    runs = []
    for y in range(h):
        in_run = False
        start_x = 0
        for x in range(w):
            if dither_arr[y, x] == 1:
                if not in_run:
                    in_run = True
                    start_x = x
            else:
                if in_run:
                    runs.append((start_x, y, x - start_x))
                    in_run = False
        if in_run:
            runs.append((start_x, y, w - start_x))
    return runs

def compute_evenness_metric(runs, num_groups, h=340, w=300, grid_size=10):
    """
    Computes spatial distribution variance across grid_size x grid_size bins.
    PDF target: ~0.05 is good (uniform shimmering), ~0.7 is patchy.
    """
    cell_h = h / grid_size
    cell_w = w / grid_size
    
    cvs = []
    for g in range(num_groups):
        bin_counts = np.zeros((grid_size, grid_size), dtype=np.float32)
        group_runs = [r for idx, r in enumerate(runs) if idx % num_groups == g]
        if not group_runs:
            continue
        for sx, y, l in group_runs:
            cx = int(min(w - 1, sx + l / 2) // cell_w)
            cy = int(min(h - 1, y) // cell_h)
            bin_counts[cy, cx] += 1
        
        non_zero = bin_counts[bin_counts > 0]
        if len(non_zero) > 1:
            cv = np.std(non_zero) / np.mean(non_zero)
            cvs.append(cv)
            
    return np.mean(cvs) if cvs else 0.0

def build_banner_svg(dither_arr, mode="dark"):
    is_dark = (mode == "dark")
    
    # Palette definition
    bg_color = "#0A101F" if is_dark else "#F8FAFC"
    panel_bg = "#0D1527" if is_dark else "#FFFFFF"
    outer_border = "#22D3EE" if is_dark else "#0891B2"
    border_opacity = "0.28" if is_dark else "0.3"
    panel_border = "#0891B2" if is_dark else "#0284C7"
    panel_border_opacity = "0.35" if is_dark else "0.25"
    
    portrait_color = "#A78BFA" if is_dark else "#7C3AED"
    title_color = "#22D3EE" if is_dark else "#0891B2"
    label_color = "#22D3EE" if is_dark else "#0891B2"
    leader_color = "#0891B2" if is_dark else "#94A3B8"
    accent_green = "#10B981" if is_dark else "#059669"
    val_white = "#E2E8F0" if is_dark else "#0F172A"
    val_blue = "#38BDF8" if is_dark else "#0284C7"
    live_red = "#EF4444" if is_dark else "#DC2626"
    sub_text = "#64748B" if is_dark else "#64748B"
    
    runs = generate_runs(dither_arr)
    # Shuffle runs with fixed seed for deterministic, perfectly even distribution
    rng = random.Random(42)
    shuffled_indices = list(range(len(runs)))
    rng.shuffle(shuffled_indices)
    
    num_groups = 60
    groups = [[] for _ in range(num_groups)]
    for i, orig_idx in enumerate(shuffled_indices):
        g = i % num_groups
        groups[g].append(runs[orig_idx])
        
    evenness = compute_evenness_metric(runs, num_groups)
    print(f"[{mode.upper()}] Total dot runs: {len(runs)}, Groups: {num_groups}, Evenness: {evenness:.3f}")
    
    # Base static layer path (for permanent crispness once animated in)
    base_path_d = "".join(f"M{x} {y}h{l}v1h{-l}Z" for x, y, l in runs)
    
    # Animated intro groups
    animated_portrait_groups = []
    for g_idx in range(num_groups):
        g_runs = groups[g_idx]
        g_d = "".join(f"M{x} {y}h{l}v1h{-l}Z" for x, y, l in g_runs)
        delay = (g_idx / float(num_groups)) * 1.85  # Stagger across 1.85s
        animated_portrait_groups.append(
            f'      <g opacity="0">\n'
            f'        <animate attributeName="opacity" values="0;1" dur="0.35s" begin="{delay:.2f}s" fill="freeze" />\n'
            f'        <path d="{g_d}" fill="{portrait_color}" shape-rendering="crispEdges" />\n'
            f'      </g>'
        )
    anim_groups_str = "\n".join(animated_portrait_groups)
    
    # SYSTEM.INFO rows configuration
    # (Label, Value, Value Color, Category Separator After)
    rows_data = [
        ("Subject", "Adith S Kumar", accent_green, False),
        ("Role", "Data Science Undergraduate", val_white, False),
        ("Origin", "Kerala, India", val_white, False),
        ("Education", "Mar Athanasius College of Eng.", val_white, False),
        ("Status", "Building + Learning + Shipping", accent_green, False),
        ("ToolChain", "VS Code, Git, GitHub, Postman, IntelliJ", val_white, True),
        
        ("Core.Lang", "Python, Java, JavaScript, TypeScript, C, SQL", portrait_color, False),
        ("Core.Frontend", "React.js, TypeScript, Vite, HTML5, CSS3", val_white, False),
        ("Core.Backend", "Spring Boot, FastAPI, Node.js, Express", val_white, False),
        ("Core.Database", "MySQL, SQLite, Firebase, PostgreSQL", val_white, False),
        ("Core.Infra", "GitHub Actions, Vercel, Git", val_white, True),
        
        ("Grid.Mail", "adithskumar777@gmail.com", val_blue, False),
        ("Grid.Portfolio", "Coming Soon", sub_text, False),
        ("Grid.LinkedIn", "in/adith-s-kumar-85b08633b", val_blue, False),
        ("Grid.GitHub", "CipherX-Adith", accent_green, False),
    ]
    
    row_lines = []
    cur_y = 132
    x_start = 484
    x_end = 1136
    char_w = 8.42  # advance width for JetBrains Mono font-size 14
    
    for label, val, color, has_sep in rows_data:
        label_w = round(len(label) * char_w, 1)
        val_w = round(len(val) * char_w, 1)
        lead_x1 = round(x_start + label_w + 10, 1)
        lead_x2 = round(x_end - val_w - 10, 1)
        
        row_svg = (
            f'      <!-- {label} -->\n'
            f'      <text x="{x_start}" y="{cur_y}" font-family="\'JetBrains Mono\', \'Fira Code\', \'Courier New\', monospace" font-size="14" font-weight="600" fill="{label_color}" textLength="{label_w}" lengthAdjust="spacingAndGlyphs">{label}</text>\n'
            f'      <line x1="{lead_x1}" y1="{cur_y - 4}" x2="{lead_x2}" y2="{cur_y - 4}" stroke="{leader_color}" stroke-opacity="0.32" stroke-dasharray="2,6" stroke-width="2" stroke-linecap="round" />\n'
            f'      <text x="{x_end}" y="{cur_y}" text-anchor="end" font-family="\'JetBrains Mono\', \'Fira Code\', monospace" font-size="14" font-weight="500" fill="{color}" textLength="{val_w}" lengthAdjust="spacingAndGlyphs">{val}</text>'
        )
        row_lines.append(row_svg)
        cur_y += 24
        
        if has_sep:
            sep_y = cur_y - 12
            row_lines.append(f'      <line x1="{x_start}" y1="{sep_y}" x2="{x_end}" y2="{sep_y}" stroke="{leader_color}" stroke-opacity="0.16" stroke-dasharray="4,6" stroke-width="1" />')
            cur_y += 6
            
    system_info_rows_str = "\n".join(row_lines)
    
    svg_content = f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1180 610" width="100%" height="100%">
  <defs>
    <style>
      @import url('https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;500;600;700&amp;display=swap');
      text {{
        font-family: 'JetBrains Mono', 'Fira Code', 'Courier New', monospace;
      }}
      @keyframes pulseLive {{
        0%, 100% {{ opacity: 1; transform: scale(1); }}
        50% {{ opacity: 0.3; transform: scale(0.9); }}
      }}
      .live-dot {{
        animation: pulseLive 2s cubic-bezier(0.4, 0, 0.6, 1) infinite;
        transform-origin: 612px 84px;
      }}
    </style>
    <filter id="subtleGlow" x="-10%" y="-10%" width="120%" height="120%">
      <feGaussianBlur stdDeviation="3" result="blur" />
      <feComposite in="SourceGraphic" in2="blur" operator="over" />
    </filter>
  </defs>

  <!-- Background Window Container -->
  <rect width="1180" height="610" rx="12" fill="{bg_color}" stroke="{outer_border}" stroke-opacity="{border_opacity}" stroke-width="1.5" />

  <!-- Terminal Header Bar -->
  <rect width="1180" height="44" rx="12" fill="{panel_bg}" fill-opacity="0.75" />
  <circle cx="28" cy="22" r="6" fill="#EF4444" />
  <circle cx="48" cy="22" r="6" fill="#F59E0B" />
  <circle cx="68" cy="22" r="6" fill="#10B981" />
  <text x="102" y="27" font-size="13" font-weight="600" fill="{title_color}" letter-spacing="1">profile.sh --live</text>
  <line x1="0" y1="44" x2="1180" y2="44" stroke="{panel_border}" stroke-opacity="0.3" stroke-width="1" />

  <!-- ================= LEFT PANEL: VISUAL.MAP (~38%) ================= -->
  <g id="left-panel">
    <!-- Frame Box -->
    <rect x="20" y="60" width="420" height="525" rx="8" fill="{panel_bg}" stroke="{panel_border}" stroke-opacity="{panel_border_opacity}" stroke-width="1" />
    
    <!-- Frame Header -->
    <text x="38" y="88" font-size="13" font-weight="700" fill="{title_color}" letter-spacing="1.5">VISUAL.MAP</text>
    <text x="362" y="88" font-size="11" font-weight="500" fill="{panel_border}" letter-spacing="0.5">[300x340]</text>
    <line x1="20" y1="102" x2="440" y2="102" stroke="{panel_border}" stroke-opacity="0.25" stroke-width="1" />

    <!-- Dither Portrait Canvas (300x340 placed at x=80, y=115) -->
    <g transform="translate(80, 115)">
      <!-- Duplicate Base Layer (ensures solid rendering after intro animation) -->
      <g opacity="0">
        <animate attributeName="opacity" values="0;1" dur="0.2s" begin="2.1s" fill="freeze" />
        <path d="{base_path_d}" fill="{portrait_color}" shape-rendering="crispEdges" />
      </g>
      
      <!-- 60 Interleaved Animated Influx Groups (~2s shimmering intro) -->
{anim_groups_str}
    </g>

    <!-- Bottom Readout Diagnostics -->
    <text x="38" y="482" font-size="11" font-weight="600" fill="{panel_border}">MODE: 1-BIT DITHER [SERPENTINE]</text>
    <text x="38" y="504" font-size="11" font-weight="600" fill="{accent_green}">RESOLUTION: 102,000 PTS [ACTIVE]</text>
    <text x="38" y="526" font-size="11" font-weight="600" fill="{portrait_color}">STATUS: SYNCHRONIZED</text>
    <rect x="38" y="542" width="384" height="6" rx="3" fill="#15203B" opacity="0.6" />
    <rect x="38" y="542" width="290" height="6" rx="3" fill="{title_color}" opacity="0.85" />
  </g>

  <!-- ================= RIGHT PANEL: SYSTEM.INFO (~62%) ================= -->
  <g id="right-panel">
    <!-- Frame Box -->
    <rect x="460" y="60" width="700" height="525" rx="8" fill="{panel_bg}" stroke="{panel_border}" stroke-opacity="{panel_border_opacity}" stroke-width="1" />
    
    <!-- Frame Header -->
    <text x="484" y="88" font-size="13" font-weight="700" fill="{title_color}" letter-spacing="1.5">SYSTEM.INFO</text>
    
    <!-- Pulsing LIVE badge -->
    <g class="live-dot">
      <circle cx="612" cy="84" r="4.5" fill="{live_red}" />
      <circle cx="612" cy="84" r="8" fill="{live_red}" opacity="0.25" />
    </g>
    <text x="626" y="88" font-size="12" font-weight="700" fill="{live_red}" letter-spacing="1">LIVE</text>
    
    <!-- Colored Handle Pill -->
    <rect x="1004" y="73" width="138" height="24" rx="12" fill="{title_color}" fill-opacity="0.12" stroke="{title_color}" stroke-opacity="0.6" stroke-width="1" />
    <text x="1073" y="89" text-anchor="middle" font-size="12" font-weight="700" fill="{title_color}">@CipherX-Adith</text>
    
    <line x1="460" y1="102" x2="1160" y2="102" stroke="{panel_border}" stroke-opacity="0.25" stroke-width="1" />

    <!-- SYSTEM.INFO Telemetry Rows with Dynamic Dotted Leaders -->
    <g id="telemetry-rows">
{system_info_rows_str}
    </g>

    <!-- Bottom Telemetry Status -->
    <line x1="484" y1="524" x2="1136" y2="524" stroke="{panel_border}" stroke-opacity="0.2" stroke-width="1" />
    <text x="484" y="546" font-size="11" font-weight="600" fill="{accent_green}">&gt; uptime: 24/7 // ping: 12ms // state: optimal</text>
    <text x="1136" y="546" text-anchor="end" font-size="11" font-weight="600" fill="{panel_border}">SHA-256: [OK]</text>
  </g>
</svg>
'''
    return svg_content

if __name__ == "__main__":
    dark_npy = r"C:\Users\adith\.gemini\antigravity\brain\44fd1b25-8c21-484f-9583-59d6d048684c\scratch\dither_dark_final.npy"
    light_npy = r"C:\Users\adith\.gemini\antigravity\brain\44fd1b25-8c21-484f-9583-59d6d048684c\scratch\dither_light_final.npy"
    
    dither_dark = np.load(dark_npy)
    dither_light = np.load(light_npy)
    
    out_dir = r"D:\files\github-profile\CipherX-Adith\assets"
    
    # 1. Dark banner
    dark_svg = build_banner_svg(dither_dark, mode="dark")
    dark_path = os.path.join(out_dir, "banner-dark.svg")
    with open(dark_path, "w", encoding="utf-8") as f:
        f.write(dark_svg)
    print(f"Generated: {dark_path} ({os.path.getsize(dark_path)/1024:.1f} KB)")
    
    # 2. Light banner
    light_svg = build_banner_svg(dither_light, mode="light")
    light_path = os.path.join(out_dir, "banner-light.svg")
    with open(light_path, "w", encoding="utf-8") as f:
        f.write(light_svg)
    print(f"Generated: {light_path} ({os.path.getsize(light_path)/1024:.1f} KB)")
