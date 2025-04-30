import os
import json
import struct
import folder_paths
from collections import OrderedDict

# Get the path to the LoRA models
lora_path = folder_paths.get_folder_paths("loras")[0]

class LoraTriggerExtractor:
    def __init__(self):
        """Initialize the LoRA trigger word extractor."""
        pass
    
    def extract_trigger_words(self, file_path):
        """
        Extract trigger words from a LoRA safetensors file, sorted by frequency.
        
        Args:
            file_path: Path to the .safetensors file
            
        Returns:
            OrderedDict of trigger words and their frequencies, sorted by frequency (highest first)
            Returns empty dict if no metadata or tag frequency information is found
        """
        try:
            with open(file_path, "rb") as f:
                # Read header length (first 8 bytes)
                header_length = struct.unpack('<Q', f.read(8))[0]
                
                # Read the header data
                header_data = f.read(header_length)
                
                # Parse the header JSON
                header = json.loads(header_data)
                
                # Check if metadata exists
                if "__metadata__" not in header:
                    print(f"No metadata found in {file_path}")
                    return {}
                    
                metadata = header["__metadata__"]
                
                # Check for tag frequency data
                if "ss_tag_frequency" not in metadata:
                    print(f"No tag frequency data found in {file_path}")
                    return {}
                    
                # Get and parse tag frequency data
                tag_freq_str = metadata["ss_tag_frequency"]
                tag_freq = json.loads(tag_freq_str)
                
                # Convert to ordered dict and sort by frequency (highest first)
                sorted_tags = OrderedDict(sorted(tag_freq.items(), key=lambda x: int(x[1]), reverse=True))
                
                return sorted_tags
                
        except Exception as e:
            print(f"Error processing {file_path}: {str(e)}")
            return {}

    def get_top_percent_triggers(self, file_path, top_percent=20):
        """
        Get the top percentage of trigger words from a LoRA file.
        
        Args:
            file_path: Path to the .safetensors file
            top_percent: Percentage of top trigger words to return (default: 20)
            
        Returns:
            List of top percentage of trigger words, or empty list if extraction failed
        """
        sorted_tags = self.extract_trigger_words(file_path)
        if not sorted_tags:
            return []
            
        # Calculate how many items to include
        num_items = max(1, int(len(sorted_tags) * (top_percent / 100.0)))
        
        # Return the top N tags
        return list(sorted_tags.keys())[:num_items]


class LoraAndTriggerWordsLoader:
    @classmethod
    def INPUT_TYPES(cls):
        # Get list of available LoRA models
        lora_files = [f for f in os.listdir(lora_path) if f.endswith('.safetensors')]
        
        return {
            "required": {
                "model": ("MODEL",),
                "clip": ("CLIP",),
                "select_lora": (lora_files,),
                "top_percent_trigger_words": ("INT", {"default": 20, "min": 1, "max": 100, "step": 1}),
                "lora_weight": ("FLOAT", {"default": 1.0, "min": 0.0, "max": 2.0, "step": 0.01}),
            },
        }

    RETURN_TYPES = ("MODEL", "CLIP", "STRING")
    RETURN_NAMES = ("model", "clip", "trigger_words")
    FUNCTION = "load_lora_and_extract_triggers"
    CATEGORY = "loaders"

    def load_lora_and_extract_triggers(self, model, clip, select_lora, top_percent_trigger_words, lora_weight):
        # Full path to the selected LoRA
        lora_file_path = os.path.join(lora_path, select_lora)
        
        # Load the LoRA model
        # This uses ComfyUI's built-in LoRA loading functionality
        import comfy.sd
        model, clip = comfy.sd.load_lora(model, clip, lora_file_path, lora_weight)
        
        # Extract trigger words
        extractor = LoraTriggerExtractor()
        trigger_words = extractor.get_top_percent_triggers(
            lora_file_path, 
            top_percent=top_percent_trigger_words
        )
        
        # Join trigger words into a string for adding to the prompt
        trigger_words_str = ", ".join(trigger_words)
        
        print(f"Loaded LoRA: {select_lora}")
        print(f"Extracted trigger words: {trigger_words_str}")
        
        return (model, clip, trigger_words_str)


# Node class for displaying the trigger words in the UI
class DisplayLoraTriggersNode:
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "trigger_words": ("STRING", {"multiline": True}),
            },
        }

    RETURN_TYPES = ()
    FUNCTION = "display_triggers"
    CATEGORY = "utils"

    def display_triggers(self, trigger_words):
        return {}


# This is how ComfyUI registers nodes
NODE_CLASS_MAPPINGS = {
    "LoraAndTriggerWordsLoader": LoraAndTriggerWordsLoader,
    "DisplayLoraTriggersNode": DisplayLoraTriggersNode,
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "LoraAndTriggerWordsLoader": "LoRA and Trigger Words Loader",
    "DisplayLoraTriggersNode": "Display LoRA Trigger Words",
}
