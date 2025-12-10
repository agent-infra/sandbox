import type { RawResponse } from "./RawResponse.js";

/**
 * The response of an API call.
 * It is a successful response or a failed response.
 */
export type APIResponse<Success, Failure> = SuccessfulResponse<Success> | FailedResponse<Failure>;

export interface SuccessfulResponse<T> {
    ok: true;
    body: T;
    /**
     * @deprecated Use `rawResponse` instead
     */
    headers?: Record<string, any>;
    rawResponse: RawResponse;
}

export interface FailedResponse<T> {
    ok: false;
    error: T;
    rawResponse: RawResponse;
}

/**
 * Type guard to check if a response is successful
 */
export function isSuccessfulResponse<Success, Failure>(
    response: APIResponse<Success, Failure>
): response is SuccessfulResponse<Success> {
    return response.ok === true;
}

/**
 * Type guard to check if a response is failed
 */
export function isFailedResponse<Success, Failure>(
    response: APIResponse<Success, Failure>
): response is FailedResponse<Failure> {
    return response.ok === false;
}
