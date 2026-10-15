"""Shared settings for the WWI grading experiment."""

from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
MODEL_NAME = "openai/gpt-oss-120b"
MAE_TARGET = 1.0
