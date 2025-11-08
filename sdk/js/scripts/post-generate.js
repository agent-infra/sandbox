#!/usr/bin/env node
/**
 * Post-generation script to fix TypeScript type errors in Fern-generated code
 */

const fs = require('fs');
const path = require('path');

const srcDir = path.join(__dirname, '..', 'src');

console.log('🔧 Fixing Fern-generated TypeScript type errors...');

// Fix 1: Headers.ts - Replace HeadersIterator with IterableIterator
const headersPath = path.join(srcDir, 'core/fetcher/Headers.ts');
if (fs.existsSync(headersPath)) {
    let headersContent = fs.readFileSync(headersPath, 'utf8');
    headersContent = headersContent.replace(/HeadersIterator</g, 'IterableIterator<');
    fs.writeFileSync(headersPath, headersContent, 'utf8');
    console.log('✓ Fixed Headers.ts');
}

// Fix 2: FormDataWrapper.ts - Add type assertions for Buffer/BlobPart
const formDataPath = path.join(srcDir, 'core/form-data-utils/FormDataWrapper.ts');
if (fs.existsSync(formDataPath)) {
    let formDataContent = fs.readFileSync(formDataPath, 'utf8');

    // Fix buffer conversions
    formDataContent = formDataContent.replace(
        /return new Blob\(\[buffer\], \{ type: contentType \}\);/g,
        'return new Blob([buffer as BlobPart], { type: contentType });'
    );

    // Fix value conversions in isBuffer branch
    formDataContent = formDataContent.replace(
        /if \(isBuffer\(value\)\) \{\s+return new Blob\(\[value\], \{ type: contentType \}\);/g,
        'if (isBuffer(value)) {\n        return new Blob([value as BlobPart], { type: contentType });'
    );

    // Fix value conversions in isArrayBufferView branch
    formDataContent = formDataContent.replace(
        /if \(isArrayBufferView\(value\)\) \{\s+return new Blob\(\[value\], \{ type: contentType \}\);/g,
        'if (isArrayBufferView(value)) {\n        return new Blob([value as BlobPart], { type: contentType });'
    );

    fs.writeFileSync(formDataPath, formDataContent, 'utf8');
    console.log('✓ Fixed FormDataWrapper.ts');
}

// Fix 3: Add providers export to index.ts if not present
const indexPath = path.join(srcDir, 'index.ts');
if (fs.existsSync(indexPath)) {
    let indexContent = fs.readFileSync(indexPath, 'utf8');

    if (!indexContent.includes('export * from "./providers"')) {
        // Add providers export
        indexContent = indexContent.trimEnd() + '\n\n// Volcengine Provider\nexport * from "./providers";\n';
        fs.writeFileSync(indexPath, indexContent, 'utf8');
        console.log('✓ Added providers export to index.ts');
    } else {
        console.log('✓ Providers export already present in index.ts');
    }
}

console.log('✅ All type fixes applied successfully!');
