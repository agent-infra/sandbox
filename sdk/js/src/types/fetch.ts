// Type definitions for fetch API in Node.js environment
export type BodyInit = string | Buffer | Uint8Array | FormData | URLSearchParams | ReadableStream<Uint8Array>;

export type HeadersInit = 
    | string[][]
    | Record<string, string>
    | Headers;