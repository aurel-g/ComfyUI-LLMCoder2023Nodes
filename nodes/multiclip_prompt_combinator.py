import comfy.utils
import json

class MulticlipPromptCombinator:
    """
    A custom node for ComfyUI that allows combining multiple CLIP text/prompt inputs
    into a single conditioning output.
    """
    
    @classmethod
    def INPUT_TYPES(cls):
        """Define the input types for this node"""
        return {
            "required": {},
            "optional": {
                "stored_prompts": ("STRING", {"default": "[]"}),
            },
            "hidden": {
                "unique_id": "UNIQUE_ID",
                "extra_pnginfo": "EXTRA_PNGINFO",
            }
        }
    
    RETURN_TYPES = ("CONDITIONING",)
    RETURN_NAMES = ("conditioning",)
    FUNCTION = "combine_prompts"
    CATEGORY = "conditioning"
    
    def ui(self, stored_prompts="[]", unique_id=None, extra_pnginfo=None):
        """Generate custom UI elements for this node"""
        try:
            prompts_list = json.loads(stored_prompts)
        except:
            prompts_list = []
            
        # Get connected inputs from extra_pnginfo
        connected_inputs = []
        if extra_pnginfo is not None and "workflow" in extra_pnginfo:
            workflow = extra_pnginfo["workflow"]
            node_id = str(unique_id)
            
            if node_id in workflow["nodes"]:
                node = workflow["nodes"][node_id]
                
                # Find all connections to this node
                for link_id, link in workflow.get("links", {}).items():
                    if link["to_node"] == node_id and link["to_socket"] != "stored_prompts":
                        from_node_id = link["from_node"]
                        from_socket = link["from_socket"]
                        
                        # Find the name/title of the source node
                        if from_node_id in workflow["nodes"]:
                            from_node = workflow["nodes"][from_node_id]
                            node_name = from_node.get("title", f"Node {from_node_id}")
                            
                            # Add to connected inputs if not already in our list
                            input_info = {
                                "id": from_node_id,
                                "socket": from_socket,
                                "name": node_name
                            }
                            
                            # Check if this input is not already stored
                            if not any(p.get("id") == from_node_id and p.get("socket") == from_socket for p in prompts_list):
                                connected_inputs.append(input_info)
        
        # UI definition with custom elements
        ui_elements = [
            {
                "type": "list",
                "name": "prompt_list",
                "label": "Connected Prompts",
                "items": prompts_list,
                "item_template": "${name} (${socket})",
                "item_actions": [
                    {
                        "name": "remove",
                        "label": "X",
                        "action": "removePrompt"
                    }
                ]
            },
            {
                "type": "button",
                "name": "refresh_connections",
                "label": "Refresh Connections",
                "action": "refreshConnections"
            },
            {
                "type": "button",
                "name": "add_button",
                "label": "ADD",
                "action": "addPrompt"
            },
            {
                "type": "hidden",
                "name": "stored_prompts",
                "value": stored_prompts
            }
        ]
        
        # Available inputs to add (connections that aren't already added)
        available_inputs = []
        for input_info in connected_inputs:
            available_inputs.append({
                "name": f"{input_info['name']} ({input_info['socket']})",
                "value": json.dumps(input_info)
            })
        
        # Custom actions
        ui_actions = {
            "removePrompt": {
                "code": """
                    const index = params.index;
                    try {
                        let currentPrompts = JSON.parse(this.value.stored_prompts);
                        currentPrompts.splice(index, 1);
                        this.value.stored_prompts = JSON.stringify(currentPrompts);
                        this.value.prompt_list = currentPrompts;
                        this.updateUI();
                    } catch (e) {
                        console.error("Error removing prompt:", e);
                    }
                """
            },
            "refreshConnections": {
                "code": """
                    // This will trigger a re-evaluation of the node and refresh connections
                    this.value.stored_prompts = this.value.stored_prompts;
                    this.updateUI();
                """
            },
            "addPrompt": {
                "code": f"""
                    const availableInputs = {json.dumps(available_inputs)};
                    
                    if (availableInputs.length > 0) {{
                        // Create a modal dialog to select from available inputs
                        const dialog = document.createElement('dialog');
                        dialog.style.padding = '20px';
                        dialog.style.borderRadius = '5px';
                        dialog.style.backgroundColor = '#2a2a2a';
                        dialog.style.color = 'white';
                        dialog.style.border = '1px solid #555';
                        
                        const title = document.createElement('h3');
                        title.textContent = 'Select Input to Add';
                        dialog.appendChild(title);
                        
                        const inputList = document.createElement('div');
                        inputList.style.display = 'flex';
                        inputList.style.flexDirection = 'column';
                        inputList.style.gap = '10px';
                        inputList.style.maxHeight = '300px';
                        inputList.style.overflowY = 'auto';
                        inputList.style.margin = '15px 0';
                        
                        availableInputs.forEach(input => {{
                            const item = document.createElement('button');
                            item.textContent = input.name;
                            item.style.padding = '8px 12px';
                            item.style.backgroundColor = '#3a3a3a';
                            item.style.border = 'none';
                            item.style.borderRadius = '4px';
                            item.style.color = 'white';
                            item.style.cursor = 'pointer';
                            
                            item.addEventListener('mouseover', () => {{
                                item.style.backgroundColor = '#4a4a4a';
                            }});
                            
                            item.addEventListener('mouseout', () => {{
                                item.style.backgroundColor = '#3a3a3a';
                            }});
                            
                            item.addEventListener('click', () => {{
                                const inputData = JSON.parse(input.value);
                                try {{
                                    let currentPrompts = JSON.parse(this.value.stored_prompts);
                                    currentPrompts.push(inputData);
                                    this.value.stored_prompts = JSON.stringify(currentPrompts);
                                    this.value.prompt_list = currentPrompts;
                                    this.updateUI();
                                }} catch (e) {{
                                    console.error("Error adding prompt:", e);
                                }}
                                dialog.close();
                            }});
                            
                            inputList.appendChild(item);
                        }});
                        
                        dialog.appendChild(inputList);
                        
                        const cancelButton = document.createElement('button');
                        cancelButton.textContent = 'Cancel';
                        cancelButton.style.padding = '8px 16px';
                        cancelButton.style.backgroundColor = '#555';
                        cancelButton.style.border = 'none';
                        cancelButton.style.borderRadius = '4px';
                        cancelButton.style.color = 'white';
                        cancelButton.style.cursor = 'pointer';
                        cancelButton.style.marginTop = '10px';
                        
                        cancelButton.addEventListener('click', () => {{
                            dialog.close();
                        }});
                        
                        dialog.appendChild(cancelButton);
                        
                        document.body.appendChild(dialog);
                        dialog.showModal();
                    }} else {{
                        // No available inputs to add
                        alert('No new input connections available. Connect more prompt nodes first.');
                    }}
                """
            }
        }
        
        return {
            "elements": ui_elements,
            "actions": ui_actions
        }
    
    def combine_prompts(self, stored_prompts="[]", unique_id=None, extra_pnginfo=None):
        """
        Combine multiple conditioning inputs into a single output
        """
        try:
            prompts_list = json.loads(stored_prompts)
        except:
            prompts_list = []
        
        if not prompts_list:
            # Return empty conditioning if no prompts connected
            return (None,)
        
        # Get the input values from the execution context
        execution_inputs = getattr(self, "inputs", {})
        
        combined_conditioning = None
        
        for prompt_info in prompts_list:
            # Get the input ID and socket
            input_id = prompt_info.get("id")
            socket = prompt_info.get("socket")
            
            # Create an input key in the format expected by ComfyUI
            input_key = f"{input_id}_{socket}"
            
            # Get the conditioning from execution inputs
            if input_key in execution_inputs:
                conditioning = execution_inputs[input_key]
                
                if conditioning is not None:
                    if combined_conditioning is None:
                        combined_conditioning = conditioning
                    else:
                        # Combine conditioning (similar to ComfyUI's ConditioningCombine node)
                        if isinstance(combined_conditioning, list) and isinstance(conditioning, list):
                            combined_conditioning.extend(conditioning)
                        elif isinstance(combined_conditioning, list):
                            combined_conditioning.append(conditioning)
                        elif isinstance(conditioning, list):
                            conditioning.insert(0, combined_conditioning)
                            combined_conditioning = conditioning
                        else:
                            combined_conditioning = [combined_conditioning, conditioning]
        
        return (combined_conditioning,)
    
    # Special methods for ComfyUI to handle dynamic inputs
    @classmethod
    def IS_CHANGED(cls, stored_prompts="[]", unique_id=None, extra_pnginfo=None):
        return float("nan")  # Always process
    
    # Allow any number of connections
    @classmethod
    def VALIDATE_INPUTS(cls, stored_prompts="[]", **kwargs):
        return True

# Register the custom node class with ComfyUI
NODE_CLASS_MAPPINGS = {
    "MulticlipPromptCombinator": MulticlipPromptCombinator
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "LLMCoderNodes::MulticlipPromptCombinator": "Multiclip Prompt Combinator"
}