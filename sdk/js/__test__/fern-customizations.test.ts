/**
 * Tests to ensure fern-generated code maintains custom modifications.
 * These tests catch when fern generate overwrites our customizations.
 *
 * Run `pnpm test` to verify before committing fern-generated changes.
 */
import { describe, it, expect } from 'vitest';
import * as fs from 'fs';
import * as path from 'path';

const SRC_DIR = path.join(__dirname, '../src');

// Helper to find files recursively
function findFiles(dir: string, pattern: RegExp): string[] {
  const results: string[] = [];

  function walk(currentDir: string) {
    const files = fs.readdirSync(currentDir);
    for (const file of files) {
      const fullPath = path.join(currentDir, file);
      const stat = fs.statSync(fullPath);
      if (stat.isDirectory()) {
        walk(fullPath);
      } else if (pattern.test(file)) {
        results.push(fullPath);
      }
    }
  }

  walk(dir);
  return results;
}

describe('Fern Customizations', () => {
  describe('BodyInit type imports', () => {
    const filesRequiringBodyInit = [
      'core/fetcher/Fetcher.ts',
      'core/fetcher/getRequestBody.ts',
      'core/fetcher/makeRequest.ts',
    ];

    filesRequiringBodyInit.forEach((filePath) => {
      it(`${filePath} should import BodyInit from types/fetch.js`, () => {
        const fullPath = path.join(SRC_DIR, filePath);
        const content = fs.readFileSync(fullPath, 'utf-8');

        expect(content).toContain('import type { BodyInit } from "../../types/fetch.js"');
      });
    });
  });

  describe('Error handling pattern in Client files', () => {
    it('should use core.isFailedResponse pattern in all Client.ts files', () => {
      const clientFiles = findFiles(path.join(SRC_DIR, 'api/resources'), /^Client\.ts$/);

      // Also include root Client.ts
      const rootClient = path.join(SRC_DIR, 'Client.ts');
      if (fs.existsSync(rootClient)) {
        clientFiles.push(rootClient);
      }

      expect(clientFiles.length).toBeGreaterThan(0);

      for (const file of clientFiles) {
        const content = fs.readFileSync(file, 'utf-8');
        const relativePath = path.relative(SRC_DIR, file);

        // Check for the correct error handling pattern
        // Should have: core.isFailedResponse(_response) ? _response.error : { reason: "unknown", errorMessage: "Unknown error" }
        if (content.includes('Error._unknown(')) {
          expect(
            content,
            `${relativePath} should use core.isFailedResponse pattern for error handling`
          ).toMatch(/core\.isFailedResponse\(_response\)\s*\?\s*_response\.error\s*:\s*\{\s*reason:\s*["']unknown["']/);

          // Should NOT have simplified pattern without isFailedResponse check
          // Pattern: Error._unknown(_response.error) without the ternary
          const simplifiedPattern = /Error\._unknown\(_response\.error\)\s*,/g;
          expect(
            content.match(simplifiedPattern),
            `${relativePath} should NOT use simplified error pattern without isFailedResponse`
          ).toBeNull();
        }
      }
    });

    it('should use full condition check before status-code switch', () => {
      const clientFiles = findFiles(path.join(SRC_DIR, 'api/resources'), /^Client\.ts$/);

      // Also include root Client.ts
      const rootClient = path.join(SRC_DIR, 'Client.ts');
      if (fs.existsSync(rootClient)) {
        clientFiles.push(rootClient);
      }

      for (const file of clientFiles) {
        const content = fs.readFileSync(file, 'utf-8');
        const relativePath = path.relative(SRC_DIR, file);

        // If file has status-code handling, it should use full condition
        if (content.includes('_response.error.reason === "status-code"')) {
          expect(
            content,
            `${relativePath} should use full condition check (!_response.ok && core.isFailedResponse)`
          ).toContain('!_response.ok && core.isFailedResponse(_response) && _response.error.reason === "status-code"');
        }
      }
    });
  });

  describe('Protected files exist', () => {
    const protectedFiles = [
      'types/fetch.ts',
      'globals.d.ts',
      'providers/index.ts',
      'providers/base.ts',
      'providers/sign.ts',
      'providers/volcengine.ts',
    ];

    protectedFiles.forEach((filePath) => {
      it(`${filePath} should exist (protected by .fernignore)`, () => {
        const fullPath = path.join(SRC_DIR, filePath);
        expect(fs.existsSync(fullPath), `${filePath} is missing - check .fernignore`).toBe(true);
      });
    });
  });

  describe('.fernignore configuration', () => {
    it('should have .fernignore in src directory', () => {
      const fernignorePath = path.join(SRC_DIR, '.fernignore');
      expect(fs.existsSync(fernignorePath)).toBe(true);
    });

    it('.fernignore should protect required paths', () => {
      const fernignorePath = path.join(SRC_DIR, '.fernignore');
      const content = fs.readFileSync(fernignorePath, 'utf-8');

      const requiredEntries = ['providers', 'index.ts', 'globals.d.ts'];
      requiredEntries.forEach((entry) => {
        expect(content, `.fernignore should contain ${entry}`).toContain(entry);
      });
    });
  });
});
