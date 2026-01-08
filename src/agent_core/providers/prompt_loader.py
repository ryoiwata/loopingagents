import os
import yaml


def get_active_system_prompt():
    """
    Load the active system prompt from YAML configuration.

    Returns:
        tuple: (template_string, parameters_dict)
    """
    # Get the project root directory (assuming this file is in src/agent_core/providers/)
    current_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.normpath(os.path.join(current_dir, "..", "..", ".."))

    # Read the active prompt from config/settings.yaml
    config_path = os.path.join(project_root, "config", "settings.yaml")
    with open(config_path, "r", encoding="utf-8") as f:
        config = yaml.safe_load(f)

    active_prompt_name = config.get("active_prompt", "v1_robot")

    # Load the corresponding prompt file
    prompt_path = os.path.join(
        project_root, "system_prompts", f"{active_prompt_name}.yaml"
    )
    with open(prompt_path, "r", encoding="utf-8") as f:
        prompt_data = yaml.safe_load(f)

    template = prompt_data.get("template", "")
    parameters = prompt_data.get("parameters", {})

    return template, parameters

