"""
Example: Using the centralized agent configuration

This example demonstrates how to use the centralized config module
to initialize agents with consistent settings.
"""

import os
import sys

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from agents.config import (
    get_api_key,
    get_model_config,
    GEMINI_MODEL_NAME,
    VISION_CONFIG,
    DIAGNOSIS_CONFIG,
)
from agents import MedicalDiagnosticGraph
import google.generativeai as genai


def example_direct_model_usage():
    """Example: Creating a Gemini model directly using config"""
    print("=" * 70)
    print("Example 1: Direct Model Usage with Config")
    print("=" * 70)
    
    # Get API key from config
    api_key = get_api_key()
    genai.configure(api_key=api_key)
    
    # Create a model using diagnosis config
    diagnosis_config = get_model_config("diagnosis")
    model = genai.GenerativeModel(
        model_name=diagnosis_config["model_name"],
        generation_config=diagnosis_config["generation_config"],
        safety_settings=diagnosis_config["safety_settings"]
    )
    
    print(f"✓ Created model: {diagnosis_config['model_name']}")
    print(f"✓ Temperature: {diagnosis_config['generation_config']['temperature']}")
    print(f"✓ Max tokens: {diagnosis_config['generation_config']['max_output_tokens']}")
    print()


def example_config_values():
    """Example: Accessing configuration values"""
    print("=" * 70)
    print("Example 2: Configuration Values")
    print("=" * 70)
    
    print(f"Primary Model: {GEMINI_MODEL_NAME}")
    print(f"Vision Model: {VISION_CONFIG['model_name']}")
    print(f"Diagnosis Temperature: {DIAGNOSIS_CONFIG['generation_config']['temperature']}")
    print()
    
    # Show all available agent configs
    print("Available agent configurations:")
    agent_types = ["router", "conversation", "diagnosis", "vision", "investigation", "recommender"]
    for agent_type in agent_types:
        config = get_model_config(agent_type)
        print(f"  - {agent_type}: {config['model_name']} "
              f"(temp={config['generation_config']['temperature']})")
    print()


def example_medical_graph_usage():
    """Example: Using MedicalDiagnosticGraph with config"""
    print("=" * 70)
    print("Example 3: Medical Diagnostic Graph with Config")
    print("=" * 70)
    
    # The graph automatically uses the centralized config
    api_key = get_api_key()
    graph = MedicalDiagnosticGraph(api_key)
    
    print("✓ MedicalDiagnosticGraph initialized")
    print("✓ All nodes are using centralized configuration")
    print("✓ Vision analyzer using:", VISION_CONFIG['model_name'])
    print("✓ Diagnosis engine using:", DIAGNOSIS_CONFIG['model_name'])
    print()


def example_custom_config():
    """Example: Creating custom configuration"""
    print("=" * 70)
    print("Example 4: Custom Configuration")
    print("=" * 70)
    
    # Get a base config and customize it
    custom_config = get_model_config("diagnosis").copy()
    
    # Make it more creative
    custom_config["generation_config"]["temperature"] = 0.7
    custom_config["generation_config"]["max_output_tokens"] = 4096
    
    print("Custom configuration created:")
    print(f"  Model: {custom_config['model_name']}")
    print(f"  Temperature: {custom_config['generation_config']['temperature']} (increased)")
    print(f"  Max tokens: {custom_config['generation_config']['max_output_tokens']} (doubled)")
    print()


def main():
    """Run all examples"""
    print("\n" + "=" * 70)
    print("CENTRALIZED AGENT CONFIGURATION EXAMPLES")
    print("=" * 70 + "\n")
    
    try:
        example_config_values()
        example_direct_model_usage()
        example_medical_graph_usage()
        example_custom_config()
        
        print("=" * 70)
        print("✓ All examples completed successfully!")
        print("=" * 70)
        
    except ValueError as e:
        print(f"\n❌ Configuration Error: {e}")
        print("\nPlease ensure GOOGLE_API_KEY is set in your .env file:")
        print("  echo 'GOOGLE_API_KEY=your-api-key-here' > .env")
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
