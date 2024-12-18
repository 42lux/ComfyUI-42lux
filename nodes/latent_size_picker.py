import torch
import comfy.model_management

MAX_RESOLUTION = 8192

class FluxEmptyLatentSizePicker:
    def __init__(self):
        self.device = comfy.model_management.intermediate_device()

    @classmethod
    def INPUT_TYPES(cls) -> dict:
        return {
            "required": {
                "resolution": ([
                    # ~3MP
                    "2688x1088 (2.92MP) - 2.39:1",
                    "2304x1280 (2.95MP) - 16:9",
                    "2240x1280 (2.87MP) - 7:4",
                    "1984x1472 (2.92MP) - 4:3",
                    "1728x1728 (2.99MP) - 1:1",
                    "1472x1984 (2.92MP) - 3:4",
                    "1280x2240 (2.87MP) - 4:7",
                    "1280x2304 (2.95MP) - 9:16",
                    # ~2MP
                    "2176x896 (1.95MP) - 2.39:1",
                    "1856x1024 (1.90MP) - 16:9",
                    "1792x1024 (1.84MP) - 7:4",
                    "1600x1216 (1.95MP) - 4:3",
                    "1408x1408 (1.98MP) - 1:1",
                    "1216x1600 (1.95MP) - 3:4",
                    "1024x1792 (1.84MP) - 4:7",
                    "1024x1856 (1.90MP) - 9:16",
                    # ~1MP
                    "1536x640 (0.98MP) - 2.39:1",
                    "1344x768 (1.03MP) - 16:9",
                    "1280x768 (0.98MP) - 7:4",
                    "1152x832 (0.96MP) - 4:3",
                    "1024x1024 (1.05MP) - 1:1",
                    "832x1152 (0.96MP) - 3:4",
                    "768x1280 (0.98MP) - 4:7",
                    "768x1344 (1.03MP) - 9:16"
                ], {"default": "2304x1280 (2.95MP) - 16:9"}),
                "batch_size": ("INT", {"default": 1, "min": 1, "max": 4096}),
                "width_override": ("INT", {"default": 0, "min": 0, "max": MAX_RESOLUTION, "step": 8}),
                "height_override": ("INT", {"default": 0, "min": 0, "max": MAX_RESOLUTION, "step": 8}),
            }
        }

    RETURN_TYPES = ("LATENT", "INT", "INT",)
    RETURN_NAMES = ("LATENT", "width", "height",)
    FUNCTION = "execute"
    CATEGORY = "42lux"

    def execute(self, resolution: str, batch_size: int, width_override: int = 0, height_override: int = 0) -> tuple:
        width, height = resolution.split(" ")[0].split("x")
        width = width_override if width_override > 0 else int(width)
        height = height_override if height_override > 0 else int(height)

        latent = torch.zeros([batch_size, 16, height // 8, width // 8], device=self.device)

        return ({"samples": latent}, width, height,)