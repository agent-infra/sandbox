/**
 * Copyright (year) Beijing Volcano Engine Technology Ltd.
 *
 * Licensed under the Apache License, Version 2.0 (the "License");
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 *
 *     http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 */

import * as crypto from 'crypto';

// Service parameters - may vary by service, but usually consistent within a service
const Service = 'apig';
const Version = '2021-03-03';
const Region = 'cn-beijing';
const Host = 'iam.volcengineapi.com';
const ContentType = 'application/x-www-form-urlencoded';

const AK_KEY = 'VOLCENGINE_ACCESS_KEY';
const SK_KEY = 'VOLCENGINE_SECRET_KEY';

const ALT_AK_KEY = 'VOLC_ACCESSKEY';
const ALT_SK_KEY = 'VOLC_SECRETKEY';

// Get credentials from environment
const AK = process.env[AK_KEY] || process.env[ALT_AK_KEY];
const SK = process.env[SK_KEY] || process.env[ALT_SK_KEY];

/**
 * Normalize query parameters for signing
 */
function normQuery(params: Record<string, any>): string {
    const keys = Object.keys(params).sort();
    const parts: string[] = [];

    for (const key of keys) {
        const value = params[key];
        if (Array.isArray(value)) {
            for (const v of value) {
                parts.push(`${encodeRFC3986(key)}=${encodeRFC3986(v)}`);
            }
        } else {
            parts.push(`${encodeRFC3986(key)}=${encodeRFC3986(value)}`);
        }
    }

    return parts.join('&');
}

/**
 * Encode string according to RFC 3986
 */
function encodeRFC3986(str: string): string {
    return encodeURIComponent(str)
        .replace(/[!'()*]/g, (c) => `%${c.charCodeAt(0).toString(16).toUpperCase()}`)
        .replace(/%20/g, '%20');
}

/**
 * HMAC-SHA256 encryption
 */
function hmacSha256(key: Buffer, content: string): Buffer {
    return crypto.createHmac('sha256', key).update(content, 'utf8').digest();
}

/**
 * SHA256 hash algorithm
 */
function hashSha256(content: string): string {
    return crypto.createHash('sha256').update(content, 'utf8').digest('hex');
}

export interface Credential {
    access_key_id: string;
    secret_access_key: string;
    service: string;
    region: string;
    session_token?: string;
}

export interface RequestParam {
    body: string;
    host: string;
    path: string;
    method: string;
    content_type: string;
    date: Date;
    query: Record<string, any>;
}

/**
 * Sign and send request to Volcengine API
 */
export async function request(
    method: string,
    date: Date,
    query: Record<string, any>,
    header: Record<string, string>,
    ak: string,
    sk: string,
    token: string | null,
    action: string,
    body: string,
    region?: string
): Promise<any> {
    // Initialize credential structure
    const credential: Credential = {
        access_key_id: ak,
        secret_access_key: sk,
        service: Service,
        region: region || Region,
    };

    if (token) {
        credential.session_token = token;
    }

    // Adjust service based on action
    if ([
        'CodeUploadCallback',
        'CreateDependencyInstallTask',
        'GetDependencyInstallTaskStatus',
        'GetDependencyInstallTaskLogDownloadURI',
        'ListTriggers',
        'CreateApplication',
        'ReleaseApplication',
        'GetApplication',
    ].includes(action)) {
        credential.service = 'vefaas';
    }

    let content_type = ContentType;
    let version = Version;

    if (method === 'POST') {
        content_type = 'application/json';
    }

    if (action === 'CreateRoute' || action === 'ListRoutes') {
        version = '2022-11-12';
    }

    // Initialize request parameters
    const requestParam: RequestParam = {
        body: body || '',
        host: Host,
        path: '/',
        method: method,
        content_type: content_type,
        date: date,
        query: { Action: action, Version: version, ...query },
    };

    // Calculate signature
    const xDate = formatDate(requestParam.date);
    const shortXDate = xDate.substring(0, 8);
    const xContentSha256 = hashSha256(requestParam.body);

    const signResult: Record<string, string> = {
        Host: requestParam.host,
        'X-Content-Sha256': xContentSha256,
        'X-Date': xDate,
        'Content-Type': requestParam.content_type,
    };

    // Calculate Signature
    const signedHeadersStr = 'content-type;host;x-content-sha256;x-date';
    const canonicalRequestStr = [
        requestParam.method.toUpperCase(),
        requestParam.path,
        normQuery(requestParam.query),
        [
            `content-type:${requestParam.content_type}`,
            `host:${requestParam.host}`,
            `x-content-sha256:${xContentSha256}`,
            `x-date:${xDate}`,
        ].join('\n'),
        '',
        signedHeadersStr,
        xContentSha256,
    ].join('\n');

    const hashedCanonicalRequest = hashSha256(canonicalRequestStr);
    const credentialScope = `${shortXDate}/${credential.region}/${credential.service}/request`;
    const stringToSign = ['HMAC-SHA256', xDate, credentialScope, hashedCanonicalRequest].join('\n');

    const kDate = hmacSha256(Buffer.from(credential.secret_access_key, 'utf8'), shortXDate);
    const kRegion = hmacSha256(kDate, credential.region);
    const kService = hmacSha256(kRegion, credential.service);
    const kSigning = hmacSha256(kService, 'request');
    const signature = hmacSha256(kSigning, stringToSign).toString('hex');

    signResult['Authorization'] = `HMAC-SHA256 Credential=${credential.access_key_id}/${credentialScope}, SignedHeaders=${signedHeadersStr}, Signature=${signature}`;

    const headers = {
        ...header,
        ...signResult,
        'X-Security-Token': token || '',
    };

    // Send HTTP request
    const url = new URL(`https://${requestParam.host}${requestParam.path}`);
    Object.entries(requestParam.query).forEach(([key, value]) => {
        url.searchParams.append(key, String(value));
    });

    const fetchOptions: RequestInit = {
        method: method,
        headers: headers,
    };

    if (method === 'POST' && requestParam.body) {
        fetchOptions.body = requestParam.body;
    }

    const response = await fetch(url.toString(), fetchOptions);
    return await response.json();
}

/**
 * Format date to ISO 8601 format (YYYYMMDDTHHMMSSZ)
 */
function formatDate(date: Date): string {
    const year = date.getUTCFullYear();
    const month = String(date.getUTCMonth() + 1).padStart(2, '0');
    const day = String(date.getUTCDate()).padStart(2, '0');
    const hours = String(date.getUTCHours()).padStart(2, '0');
    const minutes = String(date.getUTCMinutes()).padStart(2, '0');
    const seconds = String(date.getUTCSeconds()).padStart(2, '0');

    return `${year}${month}${day}T${hours}${minutes}${seconds}Z`;
}
