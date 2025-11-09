import { defineConfig } from '@rslib/core';

export default defineConfig({
  source: {
    entry: {
      index: ['./src/**/*.ts', '!./src/**/*.{test,bench}.ts'],
    },
  },
  lib: [
    {
      format: 'esm',
      syntax: 'es2021',
      bundle: false,
      dts: false,
      output: {
        distPath: './dist/esm',
      },
    },
    {
      format: 'cjs',
      syntax: 'es2021',
      bundle: false,
      dts: false,
      output: {
        distPath: './dist/cjs',
      },
    },
  ],
  output: {
    target: 'node',
    cleanDistPath: true,
    sourceMap: true,
  },
});
