"""
Vertex AI 경로로 Gemini 텍스트 생성.
인증: GOOGLE_APPLICATION_CREDENTIALS 서비스 계정 JSON 자동 사용.
"""
import config


TEXT_MODEL = "gemini-2.5-flash"


def generate_text(prompt: str, system_instruction: str = "", temperature: float = 0.9) -> str:
    """Vertex AI Gemini로 텍스트를 생성한다."""
    from vertexai.generative_models import GenerationConfig

    model  = config.get_vertex_model(TEXT_MODEL, system_instruction)
    gen_cfg = GenerationConfig(temperature=temperature)

    response = model.generate_content(prompt, generation_config=gen_cfg)
    return response.text.strip()


def parse_json_response(text: str):
    """LLM 응답에서 JSON 블록을 추출·파싱한다."""
    import json

    if "```" in text:
        parts = text.split("```")
        for part in parts[1::2]:
            cleaned = part.strip()
            if cleaned.startswith("json"):
                cleaned = cleaned[4:].strip()
            if cleaned.startswith(("{", "[")):
                return json.loads(cleaned)
    return json.loads(text)
