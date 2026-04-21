"""Конфигурация приложения: флаги возможностей (этап 7), загрузка ``.env``."""

from lang_learn.config.dotenv_load import load_dotenv_files
from lang_learn.config.feature_flags import FeatureFlags, load_feature_flags

__all__ = ["FeatureFlags", "load_dotenv_files", "load_feature_flags"]
