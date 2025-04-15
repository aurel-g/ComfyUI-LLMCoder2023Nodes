class VariableNode:
    """
    A node that defines a named variable with a value.
    """
    
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "variable_name": ("STRING", {"default": "PLANET"}),
                "variable_value": ("STRING", {"default": "MARS"})
            },
            "optional": {
                "variable_type": (["STRING", "INTEGER", "FLOAT"], {"default": "STRING"})
            }
        }
    
    RETURN_TYPES = ("VARIABLE",)  # Custom type to indicate this is a variable
    RETURN_NAMES = ("variable",)
    FUNCTION = "create_variable"
    CATEGORY = "variables"
    
    def create_variable(self, variable_name, variable_value, variable_type="STRING"):
        """
        Create a variable with name and value.
        """
        # Convert the value to the specified type
        if variable_type == "INTEGER":
            try:
                typed_value = int(variable_value)
            except ValueError:
                print(f"Warning: Could not convert '{variable_value}' to integer, using as string")
                typed_value = variable_value
        elif variable_type == "FLOAT":
            try:
                typed_value = float(variable_value)
            except ValueError:
                print(f"Warning: Could not convert '{variable_value}' to float, using as string")
                typed_value = variable_value
        else:
            typed_value = variable_value
        
        # Create a variable object
        variable = {
            "name": variable_name,
            "value": typed_value,
            "type": variable_type
        }
        
        print(f"Created variable: {variable_name} = {typed_value} ({variable_type})")
        
        return (variable,)

# Node registration
NODE_CLASS_MAPPINGS = {
    "Variable": VariableNode
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "Variable": "Variable Definition"
}