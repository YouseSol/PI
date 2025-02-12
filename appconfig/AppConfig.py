import os

import yaml


class AppConfig(object):
    config: dict | None = None

    @classmethod
    def __get_config(cls) -> dict:
        if cls.config is None:
            with open(os.environ.get("APP_CONFIG_PATH", "AppConfig.yaml"), "r") as f:
                cls.config = dict(yaml.safe_load(f))

        return cls.config

    @classmethod
    def get(cls, key: str):
        return cls.__get_config()[key]

    @classmethod
    def __class_getitem__(cls, key: str):
        return cls.get(key)
