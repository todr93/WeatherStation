from dotenv import set_key, dotenv_values


ENV_PATH = ".env"
SETTING_PREFIX = "SETTING_"


def read_settings() -> dict:
    return {
        key.replace(SETTING_PREFIX, ""): value 
        for key, value in dotenv_values(ENV_PATH).items() 
        if key.startswith("SETTING_")
        }


def save_settings(settings: dict):
    for key, value in settings.items():
        set_key(ENV_PATH, f"{SETTING_PREFIX}{key}", value)
