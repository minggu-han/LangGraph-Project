"""
配置模块：统一管理 API Key、模型名称和模型设置。

所有敏感信息和可配置项都通过 .env 文件管理。

使用方式：
    from src.config import get_model

    model = get_model()  # 使用 .env 中的所有默认配置
"""

import os
from dotenv import load_dotenv

load_dotenv()


def get_openai_api_key() -> str | None:
    """获取 OpenAI API Key"""
    return os.getenv("OPENAI_API_KEY")


def get_openai_api_base() -> str | None:
    """获取自定义 API Base URL（如使用 DeepSeek / Qwen 等兼容服务时）"""
    return os.getenv("OPENAI_API_BASE")


def get_model_name() -> str:
    """获取模型名称，默认 gpt-4o-mini"""
    return os.getenv("MODEL_NAME", "gpt-4o-mini")


def get_temperature() -> float:
    """获取温度参数，默认 0.7"""
    try:
        return float(os.getenv("MODEL_TEMPERATURE", "0.7"))
    except ValueError:
        return 0.7


def get_model(
    model_name: str | None = None,
    temperature: float | None = None,
):
    """
    获取一个 langchain-openai 兼容的 ChatModel 实例。

    优先级：参数传入 > .env 配置 > 硬编码默认值

    如果设置了 OPENAI_API_BASE，会自动使用该 base_url，
    这意味着你可以无缝切换到 DeepSeek、Qwen 等 OpenAI 兼容服务。

    Args:
        model_name: 模型名称，不传则从 .env / 默认值读取
        temperature: 温度参数，不传则从 .env / 默认值读取
    """
    from langchain_openai import ChatOpenAI

    kwargs: dict = dict(
        model=model_name or get_model_name(),
        temperature=temperature if temperature is not None else get_temperature(),
        api_key=get_openai_api_key(),
    )

    api_base = get_openai_api_base()
    if api_base:
        kwargs["base_url"] = api_base

    return ChatOpenAI(**kwargs)
