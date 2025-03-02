import os, typing as t

import yaml


class AppConfig(object):
    config: dict[str, t.Any] | None = None

    @classmethod
    def __get_config(cls) -> dict[str, t.Any]:
        if cls.config is None:
            with open(os.environ.get("APP_CONFIG_PATH", "AppConfig.yaml"), "r") as f:
                cls.config = dict(yaml.safe_load(f))

        return cls.config

    @classmethod
    def get(cls, key: str) -> t.Any:
        return cls.__get_config()[key]

    @classmethod
    def __class_getitem__(cls, key: str) -> t.Any:
        return cls.get(key)
