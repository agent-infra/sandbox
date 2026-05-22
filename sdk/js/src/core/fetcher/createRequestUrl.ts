import { toQueryString } from "../url/qs.js";

export function createRequestUrl(baseUrl: string, queryParameters?: Record<string, unknown>): string {
    const queryString = toQueryString(queryParameters, { arrayFormat: "repeat" });
    if (!queryString) {
        return baseUrl;
    }

    const url = new URL(baseUrl);
    const existingQuery = url.search.slice(1).replace(/&$/, "");
    url.search = existingQuery ? `${existingQuery}&${queryString}` : queryString;

    return url.toString();
}
