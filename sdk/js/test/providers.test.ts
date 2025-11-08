/**
 * Quick test to verify the Volcengine Provider API
 */

import { VolcengineProvider } from '../src/providers';

console.log('✓ VolcengineProvider imported successfully');

// Type checking - verify all methods exist
const provider = new VolcengineProvider('test-ak', 'test-sk');

// Verify method signatures
const hasCreateSandbox: boolean = typeof provider.createSandbox === 'function';
const hasDeleteSandbox: boolean = typeof provider.deleteSandbox === 'function';
const hasGetSandbox: boolean = typeof provider.getSandbox === 'function';
const hasListSandboxes: boolean = typeof provider.listSandboxes === 'function';
const hasCreateApplication: boolean = typeof provider.createApplication === 'function';
const hasGetApplicationReadiness: boolean = typeof provider.getApplicationReadiness === 'function';
const hasGetApigDomains: boolean = typeof provider.getApigDomains === 'function';

console.log('\n=== API Method Verification ===');
console.log('✓ createSandbox:', hasCreateSandbox);
console.log('✓ deleteSandbox:', hasDeleteSandbox);
console.log('✓ getSandbox:', hasGetSandbox);
console.log('✓ listSandboxes:', hasListSandboxes);
console.log('✓ createApplication:', hasCreateApplication);
console.log('✓ getApplicationReadiness:', hasGetApplicationReadiness);
console.log('✓ getApigDomains:', hasGetApigDomains);

const allMethodsPresent =
    hasCreateSandbox &&
    hasDeleteSandbox &&
    hasGetSandbox &&
    hasListSandboxes &&
    hasCreateApplication &&
    hasGetApplicationReadiness &&
    hasGetApigDomains;

console.log('\n=== Result ===');
if (allMethodsPresent) {
    console.log('✅ All required methods are present and callable');
    console.log('✅ Volcengine Provider API is complete');
} else {
    console.log('❌ Some methods are missing');
    process.exit(1);
}

export {};
