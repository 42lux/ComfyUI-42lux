import comfy.model_sampling

MAX_RESOLUTION = 8192

def get_latent_size(latent: dict, original_values: bool = False) -> tuple[int, int]:
    lc = latent.copy()
    size = lc["samples"].shape[3], lc["samples"].shape[2]
    if not original_values:
        size = size[0] * 8, size[1] * 8
    return size

class ModelSamplingFluxNormalized:
    @classmethod
    def INPUT_TYPES(cls) -> dict:
        return {
            "required": {
                "model": ("MODEL", {
                    "tooltip": "The model to apply sampling adjustments to"
                }),
                "latent": ("LATENT", {
                    "tooltip": "The latent to calculate image dimensions from"
                }),
                "max_shift": ("FLOAT", {
                    "default": 1.15,
                    "min": 0.0,
                    "max": 100.0,
                    "step": 0.01,
                    "tooltip": "Maximum shift value for larger resolutions"
                }),
                "base_shift": ("FLOAT", {
                    "default": 0.5,
                    "min": 0.0,
                    "max": 100.0,
                    "step": 0.01,
                    "tooltip": "Base shift value for standard resolutions"
                }),
            }
        }

    RETURN_TYPES = ("MODEL", "LATENT")
    RETURN_NAMES = ("model", "latent")
    FUNCTION = "patch"
    CATEGORY = "42lux"

    DESCRIPTION = "Adjusts model sampling parameters based on image dimensions to maintain consistent quality across different resolutions"
    OUTPUT_TOOLTIPS = ("The model with adjusted sampling parameters",)

    def patch(self, model, latent, max_shift: float, base_shift: float) -> tuple:
        m = model.clone()
        width, height = get_latent_size(latent)
        adjusted_max_shift = (base_shift - max_shift) / (256 - ((width * height) / 256)) * 3840 + base_shift

        x1 = 256
        x2 = 4096
        mm = (adjusted_max_shift - base_shift) / (x2 - x1)
        b = base_shift - mm * x1
        shift = (width * height / (8 * 8 * 2 * 2)) * mm + b

        sampling_base = comfy.model_sampling.ModelSamplingFlux
        sampling_type = comfy.model_sampling.CONST

        class ModelSamplingAdvanced(sampling_base, sampling_type):
            pass

        model_sampling = ModelSamplingAdvanced(model.model.model_config)
        model_sampling.set_parameters(shift=shift)
        m.add_object_patch("model_sampling", model_sampling)
        return (m, latent)