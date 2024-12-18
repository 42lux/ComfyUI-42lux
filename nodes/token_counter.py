from server import PromptServer

class PromptWithTokenCounter:
    MODEL_CONFIG = {
        'clip_l': {
            'key': 'l',
            'excluded_tokens': {49407, 49406},  # CLIP padding token and end token
            'max_tokens': 75,
            'display_max': '77'  # Special display value when max tokens reached
        },
        't5xxl': {
            'key': 't5xxl',
            'excluded_tokens': {0, 1},  # T5XXL padding token and end token
        }
    }

    @classmethod
    def INPUT_TYPES(cls) -> dict:
        return {
            "required": {
                "clip": ("CLIP", {"tooltip": "The CLIP model used for tokenization"}),
                "text": ("STRING", {
                    "multiline": True,
                    "tooltip": "The text to count tokens for. Supports dynamic prompts and embeddings."
                }),
                "model": (list(cls.MODEL_CONFIG.keys()), {
                    "tooltip": "The model type to count tokens for:\nclip_l: CLIP-L tokenizer\nt5xxl: T5-XXL tokenizer"
                }),
            },
            "hidden": {"unique_id": "UNIQUE_ID"},
        }

    RETURN_TYPES = ("STRING", "STRING")
    RETURN_NAMES = ("token_count", "text")
    FUNCTION = "count_tokens"
    CATEGORY = "42lux"
    OUTPUT_NODE = True
    DESCRIPTION = "Counts the number of tokens in a text prompt for different model tokenizers. Excludes padding and special tokens from the count."
    OUTPUT_TOOLTIPS = (
        "The number of tokens in the input text (excluding padding/special tokens)",
        "The input text (passed through unchanged)"
    )

    def _get_token_count(self, tokens: list, model_config: dict) -> str:
        """Calculate token count based on model configuration."""
        if not tokens or len(tokens) == 0:
            return "0"
            
        batch_tokens = tokens[0]  # Assuming batch_size == 1
        excluded_tokens = model_config['excluded_tokens']
        real_tokens = [(t[0], t[1]) for t in batch_tokens if t[0] not in excluded_tokens]
        return str(len(real_tokens))

    def count_tokens(self, clip, text: str, model: str, unique_id: str) -> tuple:
        model_config = self.MODEL_CONFIG.get(model)
        if not model_config:
            result_text = "0"
        else:
            tokens = clip.tokenize(text).get(model_config['key'])
            count = self._get_token_count(tokens, model_config)
            
            # Handle special case for CLIP-L max tokens
            result_text = (model_config.get('display_max') 
                         if model == 'clip_l' and int(count) >= model_config['max_tokens'] 
                         else count)

        # Send update event
        PromptServer.instance.send_sync("42lux.token_counter.update", {
            "node": unique_id,
            "widget": "token_count",
            "text": result_text
        })

        return (result_text, text)

    @classmethod
    def IS_CHANGED(cls, clip, text: str, model: str, unique_id: str = None) -> int:
        return hash((text, model))