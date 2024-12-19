from .nodes.model_sampling import ModelSamplingFluxNormalized
from .nodes.latent_size_picker import FluxEmptyLatentSizePicker
from .nodes.token_counter import PromptWithTokenCounter
from .nodes.highresfix_scaler import FluxHighresFixScaler

NODE_CLASS_MAPPINGS = {
    "ModelSamplingFluxNormalized": ModelSamplingFluxNormalized,
    "FluxEmptyLatentSizePicker": FluxEmptyLatentSizePicker,
    "PromptWithTokenCounter": PromptWithTokenCounter,
    "FluxHighresFixScaler": FluxHighresFixScaler,
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "ModelSamplingFluxNormalized": "Model Sampling Flux Normalized",
    "FluxEmptyLatentSizePicker": "Flux Empty Latent Size Picker",
    "PromptWithTokenCounter": "Prompt with Token Counter",
    "FluxHighresFixScaler": "Flux Highres Fix Scaler",
}

WEB_DIRECTORY = "./js"

__all__ = ['NODE_CLASS_MAPPINGS', 'NODE_DISPLAY_NAME_MAPPINGS', 'WEB_DIRECTORY']