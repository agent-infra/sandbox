import { describe, it, expect, vi, beforeEach } from 'vitest';
import { FormDataWrapper, newFormData } from '../../src/core/form-data-utils/FormDataWrapper.js';

// Mock the file and json utilities
vi.mock('../../src/core/file/index.js', () => ({
  toMultipartDataPart: vi.fn().mockResolvedValue({
    data: new Uint8Array([1, 2, 3]),
    filename: 'test.txt',
    contentType: 'text/plain'
  })
}));

vi.mock('../../src/core/json.js', () => ({
  toJson: vi.fn(obj => JSON.stringify(obj))
}));

vi.mock('../../src/core/runtime/index.js', () => ({
  RUNTIME: { type: 'node' }
}));

describe('FormDataWrapper', () => {
  describe('newFormData', () => {
    it('should create a new FormDataWrapper instance', async () => {
      const formData = await newFormData();
      expect(formData).toBeInstanceOf(FormDataWrapper);
    });
  });

  describe('FormDataWrapper instance', () => {
    let formDataWrapper: FormDataWrapper;

    beforeEach(() => {
      formDataWrapper = new FormDataWrapper();
    });

    it('should have setup method', async () => {
      await expect(formDataWrapper.setup()).resolves.toBeUndefined();
    });

    it('should append string values', () => {
      formDataWrapper.append('key1', 'value1');
      formDataWrapper.append('key2', 123);
      formDataWrapper.append('key3', true);

      const request = formDataWrapper.getRequest();
      expect(request.body).toBeInstanceOf(FormData);
    });

    it('should append file values', async () => {
      const mockFile = {
        data: new Uint8Array([1, 2, 3]),
        filename: 'test.txt'
      };

      await formDataWrapper.appendFile('file', mockFile);
      
      const request = formDataWrapper.getRequest();
      expect(request.body).toBeInstanceOf(FormData);
      expect(request.duplex).toBe('half');
    });

    it('should return proper request object', () => {
      formDataWrapper.append('test', 'value');
      
      const request = formDataWrapper.getRequest();
      expect(request).toEqual({
        body: expect.any(FormData),
        headers: {},
        duplex: 'half'
      });
    });

    it('should handle different data types for append', () => {
      formDataWrapper.append('string', 'test');
      formDataWrapper.append('number', 42);
      formDataWrapper.append('boolean', false);
      formDataWrapper.append('object', { test: true });

      const request = formDataWrapper.getRequest();
      expect(request.body).toBeInstanceOf(FormData);
    });

    it('should maintain FormData interface compatibility', () => {
      const request = formDataWrapper.getRequest();
      expect(request.body).toBeInstanceOf(FormData);
      expect(typeof request.body.append).toBe('function');
      expect(typeof request.body.delete).toBe('function');
      expect(typeof request.body.get).toBe('function');
      expect(typeof request.body.set).toBe('function');
    });
  });
});