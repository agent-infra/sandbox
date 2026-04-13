/**
 * Tests for the env parameter in ShellExecRequest.
 * Validates that the env field is correctly typed and included in the request interface.
 */
import { describe, it, expect } from 'vitest';
import * as fs from 'fs';
import * as path from 'path';
import type { ShellExecRequest } from '../src/api/resources/shell/client/requests/ShellExecRequest.js';

const SRC_DIR = path.join(__dirname, '../src');

describe('ShellExecRequest env parameter', () => {
  describe('TypeScript interface', () => {
    it('should accept env as Record<string, string>', () => {
      const request: ShellExecRequest = {
        command: 'echo $MY_VAR',
        env: {
          MY_VAR: 'hello',
          PATH: '/usr/bin:/bin',
        },
      };

      expect(request.env).toEqual({
        MY_VAR: 'hello',
        PATH: '/usr/bin:/bin',
      });
      expect(request.command).toBe('echo $MY_VAR');
    });

    it('should accept env as null', () => {
      const request: ShellExecRequest = {
        command: 'ls',
        env: null,
      };

      expect(request.env).toBeNull();
    });

    it('should accept env as undefined (omitted)', () => {
      const request: ShellExecRequest = {
        command: 'ls',
      };

      expect(request.env).toBeUndefined();
    });

    it('should accept empty env object', () => {
      const request: ShellExecRequest = {
        command: 'ls',
        env: {},
      };

      expect(request.env).toEqual({});
    });

    it('should work with all other parameters combined', () => {
      const request: ShellExecRequest = {
        command: 'echo $DB_HOST',
        id: 'session-1',
        exec_dir: '/tmp',
        async_mode: false,
        timeout: 30,
        strict: true,
        no_change_timeout: 10,
        hard_timeout: 60,
        preserve_symlinks: false,
        truncate: true,
        env: {
          DB_HOST: 'localhost',
          DB_PORT: '5432',
          NODE_ENV: 'test',
        },
      };

      expect(request.env).toEqual({
        DB_HOST: 'localhost',
        DB_PORT: '5432',
        NODE_ENV: 'test',
      });
      expect(request.command).toBe('echo $DB_HOST');
      expect(request.id).toBe('session-1');
    });

    it('should handle env with special characters in values', () => {
      const request: ShellExecRequest = {
        command: 'printenv',
        env: {
          SPECIAL: 'value with spaces',
          QUOTED: '"double quoted"',
          EQUALS: 'key=value',
          EMPTY: '',
          UNICODE: 'unicode-\u00e9\u00e8\u00ea',
        },
      };

      expect(request.env?.['SPECIAL']).toBe('value with spaces');
      expect(request.env?.['QUOTED']).toBe('"double quoted"');
      expect(request.env?.['EQUALS']).toBe('key=value');
      expect(request.env?.['EMPTY']).toBe('');
      expect(request.env?.['UNICODE']).toContain('unicode-');
    });
  });

  describe('Source code verification', () => {
    it('ShellExecRequest.ts should contain env field definition', () => {
      const filePath = path.join(
        SRC_DIR,
        'api/resources/shell/client/requests/ShellExecRequest.ts'
      );
      const content = fs.readFileSync(filePath, 'utf-8');

      expect(content).toContain('env?:');
      expect(content).toContain('Record<string, string>');
      expect(content).toContain('Environment variables');
    });

    it('Shell Client.ts should send request body including env', () => {
      const filePath = path.join(
        SRC_DIR,
        'api/resources/shell/client/Client.ts'
      );
      const content = fs.readFileSync(filePath, 'utf-8');

      // The JS client sends the entire request object as body,
      // so env will be included automatically
      expect(content).toContain('body: request');
    });
  });

  describe('JSON serialization', () => {
    it('should serialize env correctly in request body', () => {
      const request: ShellExecRequest = {
        command: 'env',
        env: {
          FOO: 'bar',
          BAZ: 'qux',
        },
      };

      const json = JSON.stringify(request);
      const parsed = JSON.parse(json);

      expect(parsed.env).toEqual({ FOO: 'bar', BAZ: 'qux' });
      expect(parsed.command).toBe('env');
    });

    it('should omit env from JSON when undefined', () => {
      const request: ShellExecRequest = {
        command: 'ls',
      };

      const json = JSON.stringify(request);
      const parsed = JSON.parse(json);

      expect(parsed).not.toHaveProperty('env');
    });

    it('should include null env in JSON', () => {
      const request: ShellExecRequest = {
        command: 'ls',
        env: null,
      };

      const json = JSON.stringify(request);
      const parsed = JSON.parse(json);

      expect(parsed.env).toBeNull();
    });
  });
});
