/*
 * Copyright (c) 2025 Bytedance, Inc. and its affiliates.
 * SPDX-License-Identifier: Apache-2.0
 */

import { VolcengineProvider } from '../src/providers';

/**
 * Example usage of Volcengine Provider for sandbox management.
 *
 * This example demonstrates how to:
 * - Initialize the Volcengine provider
 * - Create a sandbox
 * - Get sandbox details
 * - List sandboxes
 * - Delete a sandbox
 */

async function main() {
    // Initialize the provider with credentials
    const provider = new VolcengineProvider(
        process.env.VOLCENGINE_ACCESS_KEY || 'your-access-key',
        process.env.VOLCENGINE_SECRET_KEY || 'your-secret-key',
        'cn-beijing',  // region
        true           // client-side validation
    );

    const functionId = 'your-function-id';

    try {
        // Create a sandbox
        console.log('Creating sandbox...');
        const sandboxId = await provider.createSandbox(functionId, {
            timeout: 30
        });
        console.log('Sandbox created:', sandboxId);

        // Get sandbox details
        console.log('\nGetting sandbox details...');
        const sandbox = await provider.getSandbox(functionId, sandboxId);
        console.log('Sandbox details:', sandbox);

        // List all sandboxes
        console.log('\nListing all sandboxes...');
        const sandboxes = await provider.listSandboxes(functionId);
        console.log('Sandboxes:', sandboxes);

        // Delete sandbox
        console.log('\nDeleting sandbox...');
        const deleteResult = await provider.deleteSandbox(functionId, sandboxId);
        console.log('Delete result:', deleteResult);

        // Example: Create an application
        console.log('\nCreating application...');
        const appId = await provider.createApplication('my-app', 'my-gateway');
        console.log('Application created:', appId);

        if (appId) {
            // Check application readiness
            console.log('\nChecking application readiness...');
            const [isReady, functionId] = await provider.getApplicationReadiness(appId);
            console.log('Application ready:', isReady, 'Function ID:', functionId);
        }

    } catch (error) {
        console.error('Error:', error);
    }
}

// Run the example
if (require.main === module) {
    main().catch(console.error);
}

export { main };
