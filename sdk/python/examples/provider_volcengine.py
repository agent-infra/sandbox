#!/usr/bin/env python3
"""
Example usage of the Volcengine cloud provider for sandbox management.

This example demonstrates how to use the VolcengineProvider to create,
manage, and delete sandbox instances using the Volcengine VEFAAS API.
"""

from __future__ import print_function

import os
import sys

# Add the parent directory to Python path so we can import agent_sandbox
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from agent_sandbox.providers import VolcengineProvider


def main():
    """
    Main function demonstrating Volcengine provider usage.
    """
    # Configuration - replace with your actual credentials
    access_key = os.getenv("VOLC_ACCESSKEY")
    secret_key = os.getenv("VOLC_SECRETKEY")
    region = os.getenv("VOLCENGINE_REGION", "cn-beijing")
    
    # Initialize the Volcengine provider
    provider = VolcengineProvider(
        access_key=access_key,
        secret_key=secret_key,
        region=region
    )
    
    print("=== Volcengine Sandbox Provider Example ===\n")
    
    function_id = "yatoczqh"
    
    print("1. Creating a sandbox...")
    sandbox_id = provider.create_sandbox(function_id=function_id)
    print(f"Create response: {sandbox_id}")
  
    
    # Example 2: List all sandboxes for the function
    print("2. Listing all sandboxes for function...")
    list_response = provider.list_sandboxes(function_id=function_id)
    
    print(f"Number of sandboxes: {len(list_response)}")
    
    print(f"3. Get sandbox details {sandbox_id}")
    get_response = provider.get_sandbox(function_id=function_id, sandbox_id=sandbox_id)
    print(f"Get response: {get_response}")
    
    # Example 4: Delete the sandbox
    print(f"4. Deleting sandbox '{sandbox_id}'...")
    delete_response = provider.delete_sandbox(function_id=function_id, sandbox_id=sandbox_id)
    print(f"Delete response: {delete_response}")
    
    print("=== Example completed ===")


if __name__ == "__main__":
    main()
