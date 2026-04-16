import { toQueryString } from "../url/qs.js";

export function createRequestUrl(baseUrl: string, queryParameters?: Record<string, unknown>): string {
    const queryString = toQueryString(queryParameters, { arrayFormat: "repeat" });
    if (!queryString) {
        return baseUrl;
    }
    const separator = baseUrl.includes("?") ? "&" : "?";
    return `${baseUrl}${separator}${queryString}`;
}
