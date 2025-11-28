from .openai_model import OpenAILLM
from configs.model_config import ModelConfig

MODEL_REGISTRY = {
    "openai": OpenAILLM
}

class ModelFactory:
    def __init__(self):
        self.models = MODEL_REGISTRY
    
    def get_model(self, model_config: ModelConfig):
        return self.models[model_config.model_type.value](model_config)