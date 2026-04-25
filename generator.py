import os
from openai import OpenAI
from dotenv import load_dotenv
from config import MODEL, THEMES, LENGTHS

load_dotenv()


def _build_prompt(theme: str, keywords: list[str], length: str) -> str:
    word_count = LENGTHS[length]
    theme_description = THEMES[theme]
    keyword_hint = ""
    if keywords:
        kw_joined = ", ".join(keywords)
        keyword_hint = f" Puoi trarre ispirazione dai seguenti elementi: {kw_joined}."

    return (
        f"Scrivi una fiaba originale per bambini di circa {word_count} parole. "
        f"Il tema è: {theme_description}.{keyword_hint} "
        "La storia deve avere un inizio, uno svolgimento e una morale finale positiva. "
        "Usa un linguaggio semplice, vivace e adatto a bambini. Scrivi in italiano. "
        "Inizia la risposta con 'TITOLO: ' seguito dal titolo della fiaba su una riga separata, "
        "poi lascia una riga vuota e scrivi il testo della fiaba."
    )


def _parse_response(text: str) -> tuple[str, str]:
    lines = text.strip().split("\n", 2)
    if lines and lines[0].upper().startswith("TITOLO:"):
        title = lines[0].split(":", 1)[1].strip()
        body = "\n".join(lines[1:]).strip()
        return title, body
    return "Fiaba", text.strip()


def generate_story(theme: str, keywords: list[str], length: str) -> tuple[str, str]:
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise EnvironmentError(
            "Variabile d'ambiente OPENAI_API_KEY non trovata. "
            "Impostala nel file .env o nell'ambiente di sistema."
        )

    client = OpenAI(api_key=api_key)

    response = client.chat.completions.create(
        model=MODEL,
        messages=[
            {
                "role": "system",
                "content": (
                    "Sei un narratore creativo specializzato in fiabe per bambini. "
                    "Scrivi sempre in italiano con un tono caldo, immaginativo e positivo."
                ),
            },
            {
                "role": "user",
                "content": _build_prompt(theme, keywords, length),
            },
        ],
        temperature=0.9,
    )

    return _parse_response(response.choices[0].message.content.strip())
