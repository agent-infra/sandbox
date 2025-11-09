/**
 * Type declarations for browser globals used in Fern-generated cross-platform code.
 * These are only used for environment detection and won't run in Node.js.
 */

declare const window: {
  document: any;
  navigator: {
    userAgent: string;
  };
} | undefined;

declare const navigator: {
  product: string;
  userAgent?: string;
} | undefined;
