import math
import comfy.utils
import torch
import numpy as np
from PIL import Image, ImageChops

class FluxHighresFixScaler:
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "image": ("IMAGE",),
                "vae": ("VAE",),
                "target_resolution": (["4MP", "5MP", "6MP", "7MP"],),
                "upscale_method": (["nearest-exact", "bilinear", "area", "bicubic", "lanczos"],),
                "noise_scale": ("FLOAT", {"default": 0.40, "min": 0.00, "max": 100.00, "step": 0.01}),
                "blend_opacity": ("INT", {"default": 20, "min": 0, "max": 100}),
            },
            "optional": {
                "mask": ("MASK",),
            }
        }

    RETURN_TYPES = ("LATENT",)
    FUNCTION = "scale_and_encode"
    CATEGORY = "42lux"

    def tensor_to_pil(self, tensor_image):
        tensor_image = tensor_image.squeeze(0)
        pil_image = Image.fromarray((tensor_image.cpu().numpy() * 255).astype(np.uint8))
        return pil_image

    def pil_to_tensor(self, pil_image):
        return torch.from_numpy(np.array(pil_image).astype(np.float32) / 255).unsqueeze(0)

    def generate_gaussian_noise(self, width, height, noise_scale=0.05):
        noise = np.random.normal(128, 128 * noise_scale, (height, width, 3)).astype(np.uint8)
        return Image.fromarray(noise)

    def soft_light_blend(self, base_image, noise_image, mask=None, opacity=15):
        noise_image = noise_image.resize(base_image.size)
        base_image = base_image.convert('RGB')
        noise_image = noise_image.convert('RGB')

        noise_blended = ImageChops.soft_light(base_image, noise_image)
        blended_image = Image.blend(base_image, noise_blended, opacity / 100)

        if mask is not None:
            mask_pil = self.tensor_to_pil(mask).convert('L')
            mask_resized = mask_pil.resize(base_image.size)
            inverted_mask = ImageChops.invert(mask_resized)
            blended_image = Image.composite(base_image, blended_image, inverted_mask)

        return blended_image

    def scale_and_encode(self, image, vae, upscale_method, target_resolution, noise_scale=0.40, blend_opacity=20, mask=None):
        # Calculate dimensions
        _, original_height, original_width, _ = image.shape
        ratio = original_width / original_height
        
        # Set target area based on selected resolution
        target_areas = {
            "4MP": 4_000_000.0,
            "5MP": 5_000_000.0,
            "6MP": 6_000_000.0,
            "7MP": 7_000_000.0
        }
        target_area = target_areas[target_resolution]
        
        new_height = int(round(math.sqrt(target_area / ratio)))
        new_width = int(round(ratio * new_height))

        # Upscale
        samples = image.movedim(-1, 1)
        scaled = comfy.utils.common_upscale(samples, new_width, new_height, upscale_method, "disabled")
        scaled = scaled.movedim(1, -1)

        # Apply noise and blend
        scaled_pil = self.tensor_to_pil(scaled)
        noise_image = self.generate_gaussian_noise(new_width, new_height, noise_scale)
        blended_image = self.soft_light_blend(scaled_pil, noise_image, mask, blend_opacity)
        blended_tensor = self.pil_to_tensor(blended_image)

        # Encode with VAE
        encoded = vae.encode(blended_tensor[:, :, :, :3])
        return ({"samples": encoded},)
