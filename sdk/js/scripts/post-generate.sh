#!/bin/bash
# Post-generation script to fix TypeScript type errors in Fern-generated code

echo "🔧 Fixing Fern-generated TypeScript type errors..."

# Fix Headers.ts - Replace HeadersIterator with IterableIterator
sed -i 's/HeadersIterator</IterableIterator</g' src/core/fetcher/Headers.ts

# Fix FormDataWrapper.ts - Add type assertions for Buffer/BlobPart
sed -i 's/return new Blob(\[buffer\], { type: contentType });/return new Blob([buffer as BlobPart], { type: contentType });/g' src/core/form-data-utils/FormDataWrapper.ts
sed -i 's/return new Blob(\[value\], { type: contentType });/return new Blob([value as BlobPart], { type: contentType });/g' src/core/form-data-utils/FormDataWrapper.ts

# Add providers export to index.ts if not present
if ! grep -q "export \* from \"./providers\"" src/index.ts; then
    echo "" >> src/index.ts
    echo "// Volcengine Provider" >> src/index.ts
    echo "export * from \"./providers\";" >> src/index.ts
fi

echo "✅ Type fixes applied successfully!"
