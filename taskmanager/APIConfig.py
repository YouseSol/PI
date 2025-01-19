import os

import yaml


class APIConfig(object):
    config: dict | None = None

    @classmethod
    def __get_config(cls) -> dict:
        if cls.config is None:
            with open(os.environ.get("API_CONFIG_PATH", "APIConfig.yaml"), "r") as f:
                cls.config = dict(yaml.safe_load(f))

        return cls.config

    @classmethod
    def get(cls, key: str):
        return cls.__get_config()[key]
