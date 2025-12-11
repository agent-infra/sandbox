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

// Service parameters
const Service = 'vefaas';
const Version = '2024-06-06';
const Region = 'cn-beijing';
const Host = 'iam.volcengineapi.com';
const ContentType = 'application/x-www-form-urlencoded';

/**
 * Normalize query parameters for signing
 */
function normQuery(params: Record<string, string | string[]>): string {
  const sortedKeys = Object.keys(params).sort();
  const parts: string[] = [];

  for (const key of sortedKeys) {
    const value = params[key];
    if (Array.isArray(value)) {
      for (const v of value) {
        parts.push(`${encodeURIComponent(key)}=${encodeURIComponent(v)}`);
      }
    } else {
      parts.push(`${encodeURIComponent(key)}=${encodeURIComponent(value)}`);
    }
  }

  return parts.join('&').replace(/\+/g, '%20');
}

/**
 * HMAC SHA256 encryption
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

interface Credential {
  access_key_id: string;
  secret_access_key: string;
  service: string;
  region: string;
  session_token?: string;
}

interface RequestParam {
  body: string;
  host: string;
  path: string;
  method: string;
  content_type: string;
  date: Date;
  query: Record<string, string>;
}

interface SignResult {
  Host: string;
  'X-Content-Sha256': string;
  'X-Date': string;
  'Content-Type': string;
  Authorization: string;
  'X-Security-Token'?: string;
}

/**
 * Sign and send HTTP request to Volcengine API
 */
export async function request(
  method: string,
  date: Date,
  query: Record<string, string>,
  header: Record<string, string>,
  ak: string,
  sk: string,
  token: string | null,
  action: string,
  body: string,
  region?: string,
  version?: string,
): Promise<any> {
  // Initialize credential
  const credential: Credential = {
    access_key_id: ak,
    secret_access_key: sk,
    service: Service,
    region: region || Region,
  };

  if (token) {
    credential.session_token = token;
  }

  // Adjust service for specific actions
  const vefaasActions = [
    'CodeUploadCallback',
    'CreateDependencyInstallTask',
    'GetDependencyInstallTaskStatus',
    'GetDependencyInstallTaskLogDownloadURI',
    'ListTriggers',
    'CreateApplication',
    'ReleaseApplication',
    'GetApplication',
  ];

  if (vefaasActions.includes(action)) {
    credential.service = 'vefaas';
  }

  let contentType = ContentType;
  let apiVersion = version || Version;

  if (method === 'POST') {
    contentType = 'application/json';
  }

  if (!version && (action === 'CreateRoute' || action === 'ListRoutes')) {
    apiVersion = '2022-11-12';
  }

  // Initialize request parameters
  const requestParam: RequestParam = {
    body: body || '',
    host: Host,
    path: '/',
    method,
    content_type: contentType,
    date,
    query: { Action: action, Version: apiVersion, ...query },
  };

  // Calculate signature
  const xDate = date
    .toISOString()
    .replace(/[-:]/g, '')
    .replace(/\.\d{3}/, '');
  const shortXDate = xDate.slice(0, 8);
  const xContentSha256 = hashSha256(requestParam.body);

  const signResult: SignResult = {
    Host: requestParam.host,
    'X-Content-Sha256': xContentSha256,
    'X-Date': xDate,
    'Content-Type': requestParam.content_type,
    Authorization: '', // Will be set later
  };

  // Calculate signature
  const signedHeadersStr = 'content-type;host;x-content-sha256;x-date';

  const canonicalRequestStr = [
    requestParam.method.toUpperCase(),
    requestParam.path,
    normQuery(requestParam.query),
    `content-type:${requestParam.content_type}`,
    `host:${requestParam.host}`,
    `x-content-sha256:${xContentSha256}`,
    `x-date:${xDate}`,
    '',
    signedHeadersStr,
    xContentSha256,
  ].join('\n');

  const hashedCanonicalRequest = hashSha256(canonicalRequestStr);
  const credentialScope = [
    shortXDate,
    credential.region,
    credential.service,
    'request',
  ].join('/');
  const stringToSign = [
    'HMAC-SHA256',
    xDate,
    credentialScope,
    hashedCanonicalRequest,
  ].join('\n');

  // Calculate signing key
  const kDate = hmacSha256(
    Buffer.from(credential.secret_access_key, 'utf8'),
    shortXDate,
  );
  const kRegion = hmacSha256(kDate, credential.region);
  const kService = hmacSha256(kRegion, credential.service);
  const kSigning = hmacSha256(kService, 'request');
  const signature = hmacSha256(kSigning, stringToSign).toString('hex');

  signResult.Authorization = `HMAC-SHA256 Credential=${credential.access_key_id}/${credentialScope}, SignedHeaders=${signedHeadersStr}, Signature=${signature}`;

  // Merge headers
  const finalHeaders = { ...header, ...signResult };
  if (token) {
    finalHeaders['X-Security-Token'] = token;
  }

  // Send HTTP request
  const url = new URL(`https://${requestParam.host}${requestParam.path}`);
  Object.entries(requestParam.query).forEach(([key, value]) => {
    url.searchParams.append(key, value);
  });

  const response = await fetch(url.toString(), {
    method: requestParam.method,
    headers: finalHeaders,
    body: requestParam.body || undefined,
  });

  return response.json();
}
