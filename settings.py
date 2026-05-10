# settings.py
SETTINGS = {
    "system_prompt": (
        "Sei un narratore creativo specializzato in fiabe per bambini. "
        "Scrivi sempre in italiano con un tono caldo, immaginativo e positivo."
    ),
    "themes": {
        "animali": {
            "label": "Animali",
            "prompt": "protagonisti animali parlanti con caratteri distinti, ambientati in boschi, fattorie o savane",
        },
        "fantasy": {
            "label": "Fantasy",
            "prompt": "magia, draghi, streghe buone o cattive, regni incantati e oggetti magici",
        },
        "avventura": {
            "label": "Avventura",
            "prompt": "esplorazioni coraggiose, viaggi in terre lontane, scoperte e sfide da superare",
        },
    },
    "reader": {
        "font_size_index": 2,
        "dark_mode": False,
        "scroll_speed": 3,
    },
    "default_length": "corta",
}
