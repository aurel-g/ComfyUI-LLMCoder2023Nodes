class WeightedAttributesFormatterNode:
    """
    A node that creates weighted attributes and formats them into a single string.
    Uses a more flexible approach to handle attribute entries.
    """
    
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                # First attribute entry is required
                "1. TEXT": ("STRING", {"default": "Hair"}),
                "   --> VALUE": ("STRING", {"default": "Brown"}),
                "   --> WEIGHT": ("FLOAT", {"default": 0.2, "min": 0.0, "max": 0.99, "step": 0.01}),
            },
            "optional": {
                # More attributes (up to 4 more)
                "2. TEXT": ("STRING", {"default": ""}),
                "   --> VALUE 2": ("STRING", {"default": ""}),
                "   --> WEIGHT 2": ("FLOAT", {"default": 0.0, "min": 0.0, "max": 0.99, "step": 0.01}),
                
                "3. TEXT": ("STRING", {"default": ""}),
                "   --> VALUE 3": ("STRING", {"default": ""}),
                "   --> WEIGHT 3": ("FLOAT", {"default": 0.0, "min": 0.0, "max": 0.99, "step": 0.01}),
                
                "4. TEXT": ("STRING", {"default": ""}),
                "   --> VALUE 4": ("STRING", {"default": ""}),
                "   --> WEIGHT 4": ("FLOAT", {"default": 0.0, "min": 0.0, "max": 0.99, "step": 0.01}),
                
                "5. TEXT": ("STRING", {"default": ""}),
                "   --> VALUE 5": ("STRING", {"default": ""}),
                "   --> WEIGHT 5": ("FLOAT", {"default": 0.0, "min": 0.0, "max": 0.99, "step": 0.01}),
                
                # Formatting options
                "low_weight_max": ("FLOAT", {"default": 0.35, "min": 0.0, "max": 0.99, "step": 0.01}),
                "medium_weight_max": ("FLOAT", {"default": 0.7, "min": 0.0, "max": 0.99, "step": 0.01}),
                "separator": ("STRING", {"default": ", "})
            }
        }
    
    RETURN_TYPES = ("STRING", "WEIGHTED_ATTRIBUTES")
    RETURN_NAMES = ("formatted_string", "weighted_attributes")
    FUNCTION = "process_attributes"
    CATEGORY = "attributes"
    
    def process_attributes(self, **kwargs):
        """
        Process weighted attributes and format them into a string.
        Takes any number of keyword arguments and processes them dynamically.
        """
        # Extract formatting options
        low_weight_max = kwargs.get("low_weight_max", 0.35)
        medium_weight_max = kwargs.get("medium_weight_max", 0.7)
        separator = kwargs.get("separator", ", ")
        
        # Validate weight thresholds
        if low_weight_max >= medium_weight_max:
            raise ValueError(f"Low weight max ({low_weight_max}) must be less than medium weight max ({medium_weight_max})")
        if medium_weight_max >= 1.0:
            raise ValueError(f"Medium weight max ({medium_weight_max}) must be less than 1.0")
        
        # Extract attribute data
        attrs = []
        
        # Process attributes by index (1 to 5)
        for i in range(1, 6):
            key = kwargs.get(f"{i}. TEXT", "")
            value = kwargs.get(f"   --> VALUE{' ' + str(i) if i > 1 else ''}", "")
            weight = kwargs.get(f"   --> WEIGHT{' ' + str(i) if i > 1 else ''}", 0.0)
            
            if key and key.strip() != "":
                attrs.append({
                    "key": key,
                    "value": value,
                    "weight": weight
                })
        
        # Format each attribute based on its weight
        formatted_items = []
        
        for attr in attrs:
            key = attr["key"]
            value = attr["value"]
            weight = attr["weight"]
            
            # Determine format based on weight
            if weight < low_weight_max:
                format_str = "({key}={value}:{weight})"
            elif weight < medium_weight_max:
                format_str = "(({key}={value}:{weight}))"
            else:
                format_str = "((({key}={value}:{weight})))"
            
            # Format the attribute
            formatted_item = format_str.format(key=key, value=value, weight=weight)
            formatted_items.append(formatted_item)
        
        # Join all formatted items with the specified separator
        result = separator.join(formatted_items)
        
        print(f"Processed {len(attrs)} attributes")
        print(f"Formatted string: {result}")
        
        return (result, attrs)

# Node registration
NODE_CLASS_MAPPINGS = {
    "WeightedAttributesFormatter": WeightedAttributesFormatterNode
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "LLMCoderNodes::WeightedAttributesFormatter": "Weighted Attributes Formatter"
}