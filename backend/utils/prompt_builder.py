"""
Art-director-level prompt builder for character sheets and scene images.
Each STYLE_PROFILES entry defines: art_style, face_note, outfit_note,
styling, mood, negative, quality_tail.
"""

# ── Style Profiles ────────────────────────────────────────────────

STYLE_PROFILES: dict = {

    "한국웹툰시트": {
        "art_style": (
            "Bright, fresh, modern digital illustration in the sensibility of contemporary "
            "Japanese and Korean illustrators. Modern popular Pixiv style. "
            "Clean cel shading, clear light and shadow, medium-weight clean outlines, "
            "crisp polished digital finish, bright luminous colors, high but clean saturation. "
            "Palette centered on sky blue, coral red, cream white."
        ),
        "face_note": (
            "Refined modern stylish Korean face. NOT overly childish moe. "
            "Beautiful detailed face, clear expressive eyes, elegant proportions."
        ),
        "outfit_note": (
            "3-4 outfit variations: (main) Korean hanbok-based modern fusion outfit — "
            "sleek hanbok silhouette with contemporary details; "
            "(alternate) casual Korean streetwear; "
            "(performance) stage outfit with vibrant color. "
            "Main outfit design MUST be identical across all panels."
        ),
        "styling": "Clean modern stylish, contemporary Korean pop aesthetic",
        "mood": "Bright, fresh, clean and uplifting",
        "negative": (
            "photorealistic, 3D render, retro texture, dark heavy tones, "
            "overly childish moe, muddy colors, Japanese text characters, watermark, logo"
        ),
        "quality_tail": (
            "masterpiece, best quality, ultra detailed, 2K, modern anime illustration, "
            "clean digital art, fresh Pixiv style, professional character design sheet, "
            "editorial magazine layout"
        ),
    },

    "시네마틱판타지": {
        "art_style": (
            "AAA game concept art combined with cinematic fantasy visual and high-end fashion editorial. "
            "Realistic body proportions, refined attractive appearance. NOT exaggerated cartoon. "
            "Realistic, highly detailed, dramatic film-quality lighting, luxurious textures, "
            "dark moody atmosphere with golden rim light and bokeh background."
        ),
        "face_note": (
            "Natural realistic Korean face like a Korean drama lead — refined and approachable, "
            "clear radiant skin, well-defined intelligent eyes, soft sharp jawline, "
            "elegant silhouette, above-average height proportions, "
            "beautiful detailed face, attractive features, expressive captivating eyes, "
            "perfect facial proportions, elegant."
        ),
        "outfit_note": (
            "3-4 outfits: (main) modern fantasy outfit with traditional hanbok motifs reinterpreted "
            "(collar lines, knots, patterns), navy/black/gold/burgundy luxurious palette; "
            "(heroine) dramatic palace-inspired outfit with layered details, "
            "embroidery, gold metallic accessories; "
            "(casual) refined modern everyday look with subtle traditional elements."
        ),
        "styling": (
            "Realistic protagonist, relatable yet clearly a standout lead. "
            "Subtle but intricate accessories. Natural clean luxurious makeup. "
            "Cinematic hair-and-cloth motion. Refined K-drama fantasy lead aesthetic."
        ),
        "mood": (
            "Realistic Korean fantasy, mysterious refined tension, "
            "urban yet traditional beauty with mystique. "
            "A protagonist intro page that embodies a whole world."
        ),
        "negative": (
            "exaggerated cartoon, flat anime, low detail, childish proportions, "
            "plastic 3D look, watermark, logo, extra fingers, deformed hands, asymmetric eyes"
        ),
        "quality_tail": (
            "masterpiece, ultra detailed, 8K, AAA game concept art, cinematic fantasy, "
            "high-end editorial, dramatic lighting, intricate costume texture, "
            "metallic ornaments, photorealistic skin, professional art book sheet"
        ),
    },

    "지브리": {
        "art_style": (
            "Studio Ghibli hand-painted style, warm soft watercolor-like backgrounds, "
            "gentle natural lighting, soft rounded forms, nostalgic wholesome atmosphere, "
            "delicate hand-drawn linework, organic flowing movement implied in still image."
        ),
        "face_note": (
            "Gentle warm expressive Ghibli-style face, natural and kind, "
            "round soft features, sincere and emotive eyes."
        ),
        "outfit_note": (
            "3 outfit variations: (main) simple natural everyday wear with earthy tones; "
            "(adventure) travel/outdoor outfit with layered fabrics; "
            "(cozy) indoor casual with soft warm palette. "
            "Main outfit consistent across all panels."
        ),
        "styling": "Natural, wholesome, hand-painted charm with a timeless storybook quality",
        "mood": "Warm, nostalgic, peaceful, magical realism, gentle wonder",
        "negative": (
            "photorealistic, 3D render, harsh neon, cyberpunk, dark horror, "
            "watermark, logo, glossy plastic, sharp angular hard lines"
        ),
        "quality_tail": (
            "masterpiece, best quality, Studio Ghibli style, hand-painted, "
            "watercolor background, soft natural lighting, Miyazaki aesthetic, "
            "organic warm tones, professional character design sheet"
        ),
    },

    "픽사3D": {
        "art_style": (
            "Pixar-quality 3D CGI rendered illustration style. "
            "Subsurface scattering skin, physically-based rendering, "
            "vibrant saturated colors, smooth organic surfaces, "
            "professional studio key light with warm fill, "
            "ultra-clean polished cinematic finish."
        ),
        "face_note": (
            "Appealing stylized 3D face, large expressive eyes, "
            "clean smooth skin, friendly warm appearance, Pixar character charm."
        ),
        "outfit_note": (
            "3 outfit variations: (everyday) colorful casual with clean readable silhouette; "
            "(special occasion) formal celebratory look; "
            "(adventure) action-ready layered outfit."
        ),
        "styling": "Appealing, friendly, cinematic 3D animation quality",
        "mood": "Optimistic, warm, adventurous, full of personality",
        "negative": (
            "2D flat, hand-drawn, painted texture, watercolor, "
            "horror, dark gritty realism, watermark, logo, uncanny valley"
        ),
        "quality_tail": (
            "masterpiece, Pixar quality, ultra detailed 3D render, "
            "subsurface scattering, studio lighting, professional CGI, "
            "vibrant appealing character design sheet"
        ),
    },

    "클레이": {
        "art_style": (
            "Stop-motion claymation style. "
            "Handcrafted clay texture visible on all surfaces, "
            "warm tactile aesthetic with organic surface imperfections, "
            "slightly chunky rounded forms, "
            "soft studio lighting revealing clay material depth."
        ),
        "face_note": (
            "Rounded clay-textured face with bright button-like eyes, "
            "charming handmade quality, tactile and warm."
        ),
        "outfit_note": (
            "3 outfit variations with distinct color blocking and clay texture: "
            "(main) colorful primary-tone outfit; "
            "(alternate) contrasting secondary palette; "
            "(festive) warm accent colors."
        ),
        "styling": "Handmade artisan toy aesthetic, playful and tactile",
        "mood": "Playful, charming, tactile, nostalgic stop-motion magic",
        "negative": (
            "smooth CGI, photorealistic, flat 2D, watercolor, "
            "watermark, logo, harsh digital look"
        ),
        "quality_tail": (
            "masterpiece, claymation style, clay texture visible, "
            "stop-motion aesthetic, tactile handmade quality, "
            "professional character design sheet"
        ),
    },

    "2D일러스트": {
        "art_style": (
            "Clean professional 2D digital illustration. "
            "Bold clean outlines, vibrant solid colors, "
            "cel shading with clear light and shadow, "
            "modern editorial illustration sensibility, "
            "flat graphic areas with subtle gradient accents."
        ),
        "face_note": (
            "Clean expressive illustrated face, clear defined features, "
            "bold readable design, beautiful proportions."
        ),
        "outfit_note": (
            "3-4 outfit variations with strong silhouettes and clear color identity: "
            "(main) stylish contemporary look; "
            "(casual) relaxed everyday; "
            "(performance) bold graphic stage outfit."
        ),
        "styling": "Bold, clean, modern graphic illustration",
        "mood": "Vibrant, energetic, modern, graphic",
        "negative": (
            "photorealistic, painterly texture, watercolor, "
            "noisy, muddy, watermark, logo"
        ),
        "quality_tail": (
            "masterpiece, best quality, clean 2D illustration, "
            "professional editorial design, bold graphic style, "
            "character design sheet, high resolution"
        ),
    },

    "수채화": {
        "art_style": (
            "Delicate watercolor illustration. "
            "Soft translucent washes, wet-on-wet bleeding edges, "
            "visible paper texture, luminous pastel tones, "
            "organic loose expressive brushwork, "
            "white paper highlights preserved, "
            "painterly spontaneous quality."
        ),
        "face_note": (
            "Soft watercolor face with gentle lost-and-found edges, "
            "luminous and dreamy, beautiful in an ethereal way."
        ),
        "outfit_note": (
            "3 outfit variations with harmonious pastel palette: "
            "(main) flowing soft garments with watercolor wash texture; "
            "(casual) gentle everyday tones; "
            "(special) soft romantic attire."
        ),
        "styling": "Ethereal, painterly, delicate and luminous",
        "mood": "Dreamy, romantic, gentle, poetic",
        "negative": (
            "photorealistic, harsh sharp lines, digital clean, 3D render, "
            "neon colors, watermark, logo, muddy overworked paint"
        ),
        "quality_tail": (
            "masterpiece, delicate watercolor illustration, "
            "paper texture visible, soft luminous tones, "
            "professional artist character design sheet"
        ),
    },

    "일본애니": {
        "art_style": (
            "High-quality Japanese anime illustration. "
            "Detailed clean linework, refined cel shading with multiple tone layers, "
            "brilliant saturated colors with strategic desaturation, "
            "dramatic rim lighting, detailed layered hair rendering, "
            "professional A-tier anime production quality."
        ),
        "face_note": (
            "Beautiful refined anime face, detailed layered hair, "
            "large luminous eyes with specular highlights and depth, "
            "clean sharp facial definition, elegant proportions."
        ),
        "outfit_note": (
            "3-4 outfit variations with detailed anime-style layering: "
            "(main) primary character look with accessories; "
            "(alternate) story-significant costume; "
            "(casual) school or everyday anime style."
        ),
        "styling": "Polished high-production anime with cinematic quality",
        "mood": "Dynamic, emotional, cinematic anime energy",
        "negative": (
            "low quality, rough sketch, chibi, western cartoon, "
            "photorealistic, muddy colors, watermark, logo"
        ),
        "quality_tail": (
            "masterpiece, best quality, high-end anime illustration, "
            "ultra detailed, professional key visual, "
            "A-tier anime production, character design sheet"
        ),
    },

    "시네마틱실사": {
        "art_style": (
            "Cinematic photorealistic photography style. "
            "Professional studio or on-location photography quality, "
            "dramatic Rembrandt-style or cinematic key lighting, "
            "shallow depth of field with elegant bokeh, "
            "natural realistic skin texture, "
            "film color grading, ultra-sharp detail."
        ),
        "face_note": (
            "Real Korean actress-quality face, "
            "natural beautiful features, professional elegant makeup, "
            "cinematic portrait quality."
        ),
        "outfit_note": (
            "3-4 real styled fashion outfits: "
            "(main) casual chic contemporary; "
            "(elegant) formal evening look; "
            "(street) refined street fashion."
        ),
        "styling": "High-end fashion photography meets cinematic portraiture",
        "mood": "Sophisticated, dramatic, cinematic realism",
        "negative": (
            "illustration, cartoon, anime, painted, "
            "watermark, logo, extra fingers, deformed, uncanny valley"
        ),
        "quality_tail": (
            "masterpiece, 8K photorealistic, cinematic photography, "
            "professional lighting, DSLR quality, "
            "film color grade, character reference sheet"
        ),
    },

    "빈티지필름": {
        "art_style": (
            "Vintage analog film photography aesthetic. "
            "Visible grain and film texture, "
            "warm faded color palette with muted nostalgic tones, "
            "subtle light leaks and vignette, "
            "soft focus with gentle lens aberration, "
            "1970s-1980s film photography sensibility."
        ),
        "face_note": (
            "Soft film-grain portrait face, "
            "warm nostalgic coloring, natural understated beauty."
        ),
        "outfit_note": (
            "3 looks with warm vintage color palette: "
            "(main) timeless classic style; "
            "(casual) relaxed retro casual; "
            "(special) vintage formal or festive."
        ),
        "styling": "Nostalgic, warm, analog photographic quality",
        "mood": "Nostalgic, warm, romantic, timeless",
        "negative": (
            "sharp digital HDR, clean neon, futuristic, "
            "illustration, watermark, logo"
        ),
        "quality_tail": (
            "masterpiece, vintage film photography, "
            "analog grain texture, warm faded tones, "
            "professional retro character design sheet"
        ),
    },

    "네온사이버펑크": {
        "art_style": (
            "Cyberpunk neon aesthetic digital illustration. "
            "Vibrant neon pink, cyan, purple, electric blue color palette, "
            "dark urban night atmosphere, "
            "holographic and glowing elements, "
            "high-contrast dramatic neon rim lighting, "
            "futuristic tech visual language."
        ),
        "face_note": (
            "Striking cyberpunk-styled face with neon light accents, "
            "sharp defined features, futuristic elegance."
        ),
        "outfit_note": (
            "3-4 futuristic cyberpunk outfits with tech elements: "
            "(main) street runner tactical wear with neon accents; "
            "(elite) hacker/operative sleek look; "
            "(performance) neon performer stage outfit."
        ),
        "styling": "High-tech futuristic neon urban aesthetic",
        "mood": "Edgy, electric, futuristic, neon-lit urban night",
        "negative": (
            "natural daylight pastoral, soft watercolor, "
            "medieval fantasy, watermark, logo"
        ),
        "quality_tail": (
            "masterpiece, cyberpunk neon aesthetic, ultra detailed, "
            "dramatic neon lighting, futuristic, "
            "professional character design sheet"
        ),
    },

    "판타지": {
        "art_style": (
            "Epic fantasy illustration. "
            "Painterly digital art style, "
            "dramatic magical lighting with glowing spell effects, "
            "detailed fantasy world-building elements, "
            "rich jewel-tone color palette, "
            "ornate costume and prop detailing."
        ),
        "face_note": (
            "Beautiful fantasy protagonist face with otherworldly elegance, "
            "luminous expressive eyes, refined ethereal features."
        ),
        "outfit_note": (
            "3-4 fantasy costume variations: "
            "(main) hero outfit with magical motifs; "
            "(battle) armor or combat attire with ornate detail; "
            "(ceremonial) elegant formal fantasy dress."
        ),
        "styling": "Epic fantasy world aesthetic with high painterly quality",
        "mood": "Epic, magical, adventurous, wonder-filled",
        "negative": (
            "modern contemporary setting, photorealistic photography, "
            "cyberpunk neon, flat 2D minimal, watermark, logo"
        ),
        "quality_tail": (
            "masterpiece, epic fantasy illustration, ultra detailed, "
            "magical atmosphere, ornate detail, dramatic lighting, "
            "professional fantasy character design sheet"
        ),
    },

    "미니멀모노톤": {
        "art_style": (
            "Minimalist monochrome illustration. "
            "Clean geometric linework, "
            "black, white and limited grey tones only, "
            "sophisticated negative space composition, "
            "editorial graphic art sensibility, "
            "bold clean silhouettes."
        ),
        "face_note": (
            "Elegant clean-line monochrome face, "
            "simple but highly expressive, refined minimal features."
        ),
        "outfit_note": (
            "3 outfit variations expressed in line and tone only: "
            "(main) bold graphic silhouette; "
            "(casual) clean minimal lines; "
            "(formal) geometric structured look."
        ),
        "styling": "Sophisticated minimalist graphic art",
        "mood": "Refined, sophisticated, clean, modern",
        "negative": (
            "colorful, painted texture, photorealistic, "
            "noisy, cluttered, watermark, logo"
        ),
        "quality_tail": (
            "masterpiece, minimalist monochrome, clean precise lines, "
            "professional editorial illustration, "
            "sophisticated character design sheet"
        ),
    },

    "마블코믹스": {
        "art_style": (
            "Marvel comic book style illustration. "
            "Bold dynamic ink lines, "
            "cel-shaded vibrant colors, "
            "halftone dot texture accents, "
            "dramatic action-ready hero aesthetic, "
            "strong graphic visual language."
        ),
        "face_note": (
            "Bold heroic comic-book face, "
            "strong defined features, expressive powerful eyes."
        ),
        "outfit_note": (
            "3-4 outfit variations: "
            "(main) signature hero costume with bold color; "
            "(street clothes) civilian casual look; "
            "(battle) armored or powered-up alternate design."
        ),
        "styling": "Heroic, dynamic, action comic book visual language",
        "mood": "Heroic, dynamic, bold, action-packed",
        "negative": (
            "soft watercolor, pastel, photorealistic, "
            "dark horror, watermark, logo"
        ),
        "quality_tail": (
            "masterpiece, Marvel comic book style, bold dynamic inks, "
            "vibrant colors, professional character design sheet"
        ),
    },

    "오일페인팅": {
        "art_style": (
            "Classical oil painting style. "
            "Visible brushstroke texture with impasto technique, "
            "rich warm old-master color palette, "
            "Rembrandt-style chiaroscuro lighting, "
            "varnished glowing depth, "
            "museum-quality painterly finish."
        ),
        "face_note": (
            "Classical portrait face with painterly skin texture, "
            "old-master lighting quality, warm glowing skin tones, "
            "timeless elegant beauty."
        ),
        "outfit_note": (
            "3 outfit variations richly painted: "
            "(main) period or contemporary attire in warm palette; "
            "(elegant) formal portrait attire; "
            "(casual) atmospheric everyday dress."
        ),
        "styling": "Classical museum-quality oil painting sensibility",
        "mood": "Rich, warm, classical, timeless and painterly",
        "negative": (
            "digital clean, flat, anime, cartoon, "
            "neon, watermark, logo"
        ),
        "quality_tail": (
            "masterpiece, classical oil painting, "
            "rich impasto texture, old-master quality, "
            "professional character design sheet"
        ),
    },

    "픽셀아트": {
        "art_style": (
            "Detailed pixel art style. "
            "Clean pixel grid with anti-aliased edges, "
            "limited but carefully chosen color palette, "
            "retro video game aesthetic with modern refinement, "
            "nostalgic 16-bit to 32-bit era quality."
        ),
        "face_note": (
            "Expressive pixel face with clear readable features, "
            "charming retro game sprite quality."
        ),
        "outfit_note": (
            "3-4 sprite variations: "
            "(main) primary character costume; "
            "(alternate) color-swapped variant; "
            "(special) event or story outfit."
        ),
        "styling": "Retro video game sprite aesthetic with modern polish",
        "mood": "Nostalgic, playful, retro gaming energy",
        "negative": (
            "photorealistic, smooth 3D, watercolor, "
            "blurry, anti-aliased away from pixels, watermark, logo"
        ),
        "quality_tail": (
            "masterpiece, detailed pixel art, "
            "clean pixel grid, professional sprite sheet, "
            "retro game character design sheet"
        ),
    },

    "수묵화": {
        "art_style": (
            "Korean and Chinese ink wash painting style (sumi-e / muk-hwa). "
            "Expressive minimal brushwork with dramatic negative space, "
            "black ink gradients from deep black to diluted grey, "
            "occasional subtle color wash accents, "
            "spontaneous yet controlled brushstroke energy, "
            "traditional East Asian painting sensibility."
        ),
        "face_note": (
            "Elegant ink-wash face with minimal brushstrokes "
            "capturing maximum expression, refined and poetic."
        ),
        "outfit_note": (
            "3 outfit variations rendered in ink wash: "
            "(main) traditional or contemporary flowing garment; "
            "(dynamic) movement-captured pose with ink energy; "
            "(still) meditative minimal composition."
        ),
        "styling": "Traditional East Asian ink painting with Zen-like restraint",
        "mood": "Zen, poetic, contemplative, traditional",
        "negative": (
            "colorful digital, photorealistic, anime flat color, "
            "western cartoon, watermark, logo"
        ),
        "quality_tail": (
            "masterpiece, ink wash painting, sumi-e style, "
            "expressive brushwork, traditional East Asian art, "
            "professional character design sheet"
        ),
    },
}


# ── Internal helpers ───────────────────────────────────────────────

def _get_profile(style: str) -> dict:
    return STYLE_PROFILES.get(style, {})


def _art(p: dict, fallback: str) -> str:
    return p.get("art_style") or fallback


def _neg(p: dict) -> str:
    return p.get("negative") or "watermark, logo, cropped"


def _qtail(p: dict) -> str:
    return p.get("quality_tail") or "masterpiece, best quality, high detail"


# ── Public builders ────────────────────────────────────────────────

def build_character_sheet_prompt(style: str, char_name: str, char_desc: str) -> str:
    """Multi-panel character reference sheet (used for protagonist asset sheet)."""
    p = _get_profile(style)
    if not p:
        return (
            f"Professional character reference sheet. "
            f"Character: {char_name}, {char_desc}. "
            f"Includes 6 expressions, full body front/side/back/3-4 views, "
            f"3-4 outfit variations, color palette. "
            f"Consistent face and design across all panels. "
            f"White background, labeled layout. High quality."
        )

    return (
        "You are a professional animation character designer, "
        "art director, and visual concept artist.\n\n"
        "Create a complete professional character reference sheet "
        "for a 2-minute music video protagonist.\n\n"
        f"[ART STYLE]\n{p['art_style']}\n\n"
        f"[CHARACTER]\n"
        f"Name: {char_name}\n"
        f"{char_desc}\n"
        f"{p['face_note']}\n\n"
        "[EXPRESSIONS] Include 6 face close-ups arranged in a row:\n"
        "neutral/calm, surprised, tense/alert, determined, "
        "soft warm smile, slightly tired\n\n"
        f"[OUTFITS]\n{p['outfit_note']}\n"
        "Main outfit MUST be identical across all panels.\n\n"
        "[FULL BODY] Front view, side view, back view, 3/4 view — "
        "full body not cropped, feet visible, consistent proportions\n\n"
        f"[STYLING] {p['styling']}\n"
        f"[MOOD] {p['mood']}\n"
        "[BACKGROUND] Decorative background fitting the story — "
        "not pure white, not louder than the character\n"
        "[LAYOUT] Professional concept-art book layout: "
        "large main figure on left, side panels for pose variations, "
        "expression close-ups in a row, outfit callouts, "
        "props and color palette at bottom\n\n"
        "[CONSISTENCY] Identical face, same hair, same design across ALL panels. "
        "Same art style throughout.\n\n"
        f"[STRICTLY AVOID] {p['negative']}\n\n"
        f"{p['quality_tail']}"
    )


def build_character_front_prompt(style: str, char_name: str, char_desc: str) -> str:
    """Single full-body front-view reference image (used as reference for side/back views)."""
    p = _get_profile(style)
    if not p:
        return (
            f"Full body character design, {style} style, {char_desc}, "
            "FRONT view, facing forward directly, standing pose, "
            "white background, full body visible from head to toe, "
            "clean lines, character reference sheet style"
        )

    return (
        f"{p['art_style']}\n\n"
        "Single character full-body FRONT VIEW reference image. "
        f"Character: {char_name}, {char_desc}. "
        f"{p['face_note']}\n\n"
        "FRONT VIEW: facing forward directly, neutral standing pose, "
        "full body from head to toe, feet fully visible. "
        "Clean white or neutral background. "
        "Character design reference quality — single character only, no other figures.\n\n"
        f"[STYLING] {p['styling']}\n\n"
        f"[STRICTLY AVOID] {p['negative']}, cropped body, cut-off feet, multi-panel layout\n\n"
        f"{p['quality_tail']}"
    )


def build_supporting_sheet_prompt(style: str, supp_name: str, supp_desc: str) -> str:
    """Supporting character reference sheet."""
    p = _get_profile(style)
    art   = _art(p, style)
    neg   = _neg(p)
    qtail = _qtail(p)
    face  = p.get("face_note", "")

    return (
        "Professional supporting character reference sheet, single image.\n\n"
        f"[ART STYLE]\n{art}\n\n"
        f"[CHARACTER]\n"
        f"Name: {supp_name}\n"
        f"{supp_desc}\n"
        f"{face}\n\n"
        "Sheet includes, neatly arranged in panels:\n"
        "1. Bust portrait key visual\n"
        "2. EXPRESSIONS: 3 expressions — neutral, happy, sad\n"
        "3. FULL BODY: front view and side view\n"
        "4. POSES: 2 characteristic poses\n\n"
        "CONSISTENCY: identical face, hairstyle, and outfit across ALL panels.\n"
        "White or pastel background, labeled panels.\n\n"
        f"[STRICTLY AVOID] {neg}\n\n"
        f"{qtail}"
    )


def build_assets_sheet_prompt(style: str, settings_str: str, items_str: str) -> str:
    """Production asset sheet / mood board for backgrounds and props."""
    p = _get_profile(style)
    art   = _art(p, style)
    qtail = _qtail(p)

    return (
        "Production asset sheet and mood board, single image, labeled grid layout.\n\n"
        f"[ART STYLE]\n{art}\n\n"
        f"BACKGROUNDS section — 3 environments:\n{settings_str}\n\n"
        f"PROPS section — key story items: {items_str}\n\n"
        "Clean reference-sheet layout, consistent art style throughout, "
        "white background, clearly labeled sections.\n\n"
        f"{qtail}, 4K"
    )


def build_scene_prompt_rich(
    scene: dict,
    char_base: str,
    style: str,
    style_kw_fallback: str = "",
) -> str:
    """Scene image prompt with art-director-level style description."""
    p         = _get_profile(style)
    desc      = scene.get("description", "")
    camera    = scene.get("camera", "medium shot")
    mood      = scene.get("mood", "")
    is_chorus = scene.get("is_chorus", False)
    energy    = (
        "dynamic visual composition, dramatic lighting, cinematic energy, high-impact moment"
        if is_chorus else
        "balanced atmospheric composition, subtle expressive mood lighting"
    )
    safety = (
        "tasteful artistic depiction, safe for all audiences, "
        "non-violent, poetic and metaphorical expression"
    )

    if not p:
        kw     = style_kw_fallback or style
        beauty = (
            ", beautiful detailed face, attractive features, "
            "professional character art, masterpiece quality"
            if style in ("한국웹툰시트", "시네마틱판타지") else ""
        )
        return (
            f"{char_base}, {desc}, {camera}, {kw}{beauty}, "
            f"{energy}, {safety}, 16:9 aspect ratio, high quality."
            + (f" Scene mood: {mood}." if mood else "")
        )

    mood_line = f"Scene mood: {mood}." if mood else ""

    return (
        f"{p['art_style']}\n\n"
        f"Scene: {desc}\n"
        f"Camera: {camera}\n"
        f"Character: {char_base} — same character as reference sheet, "
        "identical face and outfit\n"
        f"Composition: {energy}\n"
        f"{mood_line}\n"
        f"{safety}, 16:9 aspect ratio.\n\n"
        f"{p['quality_tail']}"
    )
