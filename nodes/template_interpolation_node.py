class TemplateInterpolationNode:
    """
    A node that performs string interpolation using variables.
    """
    
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "variable": ("VARIABLE",),  # Accept variable type
                "template_text": ("STRING", {
                    "multiline": True,
                    "default": "Hello from planet $PLANET$"
                })
            }
        }
    
    RETURN_TYPES = ("STRING",)
    RETURN_NAMES = ("interpolated_text",)
    FUNCTION = "interpolate_template"
    CATEGORY = "text"
    
    def interpolate_template(self, variable, template_text):
        """
        Replace variable placeholders in the template with their values.
        """
        # Get the variable name and value from the variable object
        variable_name = variable["name"]
        variable_value = variable["value"]
        
        # Create the placeholder pattern (e.g., $PLANET$)
        placeholder = f"${variable_name}$"
        
        # Convert value to string regardless of its type
        value_str = str(variable_value)
        
        # Replace all occurrences of the placeholder with the value
        result = template_text.replace(placeholder, value_str)
        
        print(f"Template: {template_text}")
        print(f"Variable '{variable_name}' = {value_str}")
        print(f"Result: {result}")
        
        return (result,)

# Node registration
NODE_CLASS_MAPPINGS = {
    "TemplateInterpolation": TemplateInterpolationNode
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "LLMCoderNodes::TemplateInterpolation": "String Template Interpolation"
}