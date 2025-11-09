/**
 * Volcengine cloud provider implementation for sandbox management.
 *
 * This provider uses the Volcengine VEFAAS (Volcengine Function as a Service)
 * API to manage sandbox instances.
 */

import { BaseProvider } from './base';
import { request } from './sign';

interface DomainInfo {
  domain: string;
  type?: string;
}

interface VolcengineProviderOptions {
  accessKey: string;
  secretKey: string;
  region?: string;
  clientSideValidation?: boolean;
}

export class VolcengineProvider extends BaseProvider {
  private accessKey: string;
  private secretKey: string;
  private region: string;
  private clientSideValidation: boolean;

  /**
   * Initialize the Volcengine provider.
   *
   * @param options - Configuration options
   * @param options.accessKey - Volcengine access key ID
   * @param options.secretKey - Volcengine secret access key
   * @param options.region - Volcengine region, defaults to "cn-beijing"
   * @param options.clientSideValidation - Enable client-side validation, defaults to true
   */
  constructor(options: VolcengineProviderOptions) {
    super();
    this.accessKey = options.accessKey;
    this.secretKey = options.secretKey;
    this.region = options.region || 'cn-beijing';
    this.clientSideValidation = options.clientSideValidation !== false;
  }

  /**
   * Create a new sandbox instance using Volcengine VEFAAS.
   *
   * @param functionId - The function ID for the sandbox
   * @param timeout - The timeout for the sandbox creation in minutes (default: 30)
   * @param kwargs - Additional parameters for sandbox creation
   * @returns The ID of the created sandbox or error
   */
  async createSandbox(functionId: string, timeout: number = 30, ...kwargs: any[]): Promise<any> {
    try {
      const body = JSON.stringify({
        function_id: functionId,
        timeout,
        ...kwargs[0],
      });

      const response = await request(
        'POST',
        new Date(),
        {},
        {},
        this.accessKey,
        this.secretKey,
        null,
        'CreateSandbox',
        body
      );

      return response.sandbox_id;
    } catch (error) {
      return error;
    }
  }

  /**
   * Delete an existing sandbox instance.
   *
   * @param functionId - The function ID of the sandbox
   * @param sandboxId - The ID of the sandbox to delete
   * @param kwargs - Additional parameters for sandbox deletion
   * @returns The response containing deletion status
   */
  async deleteSandbox(functionId: string, sandboxId: string, ...kwargs: any[]): Promise<any> {
    try {
      const body = JSON.stringify({
        function_id: functionId,
        sandbox_id: sandboxId,
        ...kwargs[0],
      });

      const response = await request(
        'POST',
        new Date(),
        {},
        {},
        this.accessKey,
        this.secretKey,
        null,
        'KillSandbox',
        body
      );

      return response;
    } catch (error) {
      return error;
    }
  }

  /**
   * Append ?faasInstanceName= to domain field of structured domain objects.
   */
  private appendInstanceQueryStruct(domainsInfo: DomainInfo[], instanceName: string): DomainInfo[] {
    const result: DomainInfo[] = [];

    for (const info of domainsInfo) {
      const domainStr = info.domain;
      if (!domainStr) {
        continue;
      }

      let newDomain: string;
      if (domainStr.includes('?')) {
        newDomain = `${domainStr}&faasInstanceName=${instanceName}`;
      } else {
        newDomain = `${domainStr}?faasInstanceName=${instanceName}`;
      }

      result.push({
        domain: newDomain,
        type: info.type,
      });
    }

    return result;
  }

  /**
   * Get details of an existing sandbox instance.
   *
   * @param functionId - The function ID of the sandbox
   * @param sandboxId - The ID of the sandbox to retrieve
   * @param kwargs - Additional parameters for sandbox retrieval
   * @returns The response containing sandbox details
   */
  async getSandbox(functionId: string, sandboxId: string, ...kwargs: any[]): Promise<any> {
    try {
      const body = JSON.stringify({
        function_id: functionId,
        sandbox_id: sandboxId,
        ...kwargs[0],
      });

      const response = await request(
        'POST',
        new Date(),
        {},
        {},
        this.accessKey,
        this.secretKey,
        null,
        'DescribeSandbox',
        body
      );

      const baseDomains = await this.getApigDomains(functionId);
      const domainsStruct = this.appendInstanceQueryStruct(baseDomains, sandboxId);
      response.domains = domainsStruct;

      return response;
    } catch (error) {
      return error;
    }
  }

  /**
   * List all sandbox instances for a function.
   *
   * @param functionId - The function ID to list sandboxes for
   * @param kwargs - Additional parameters for listing sandboxes
   * @returns The response containing list of sandboxes
   */
  async listSandboxes(functionId: string, ...kwargs: any[]): Promise<any> {
    try {
      const body = JSON.stringify({
        function_id: functionId,
        ...kwargs[0],
      });

      const response = await request(
        'POST',
        new Date(),
        {},
        {},
        this.accessKey,
        this.secretKey,
        null,
        'ListSandboxes',
        body
      );

      // Attach domains with instanceName query to each sandbox item
      const baseDomains = await this.getApigDomains(functionId);
      const sandboxes = response.sandboxes || [];
      const normalized: any[] = [];

      for (const sb of sandboxes) {
        const instanceId = sb.id || sb.sandbox_id;
        const domainsStruct = instanceId
          ? this.appendInstanceQueryStruct(baseDomains, instanceId)
          : baseDomains;
        sb.domains = domainsStruct;
        normalized.push(sb);
      }

      return normalized;
    } catch (error) {
      return error;
    }
  }

  /**
   * Get the UpstreamId from APIG triggers for a given function.
   *
   * @param functionId - The function ID to get triggers for
   * @returns The UpstreamId from the first APIG trigger found, or null
   */
  private async getApigTrigger(functionId: string): Promise<string | null> {
    const body = JSON.stringify({
      FunctionId: functionId,
    });

    const response = await request(
      'POST',
      new Date(),
      {},
      {},
      this.accessKey,
      this.secretKey,
      '',
      'ListTriggers',
      body
    );

    if (response && typeof response === 'object') {
      const result = response.Result || {};
      const items = result.Items || [];

      for (const item of items) {
        if (item.Type === 'apig') {
          const detailedConfig = item.DetailedConfig || '{}';
          try {
            const config = JSON.parse(detailedConfig);
            const upstreamId = config.UpstreamId;
            if (upstreamId) {
              return upstreamId;
            }
          } catch (error) {
            console.error(`Failed to parse DetailedConfig: ${detailedConfig}`);
            continue;
          }
        }
      }
    }

    return null;
  }

  /**
   * Get structured domains from APIG routes using the upstream ID.
   *
   * @param upstreamId - The upstream ID to get routes for
   * @returns List of domains from the routes, or empty list
   */
  private async getApigDomainsFromUpstream(upstreamId: string): Promise<DomainInfo[]> {
    const body = JSON.stringify({
      UpstreamId: upstreamId,
      PageSize: 100,
      PageNumber: 1,
    });

    const response = await request(
      'POST',
      new Date(),
      {},
      {},
      this.accessKey,
      this.secretKey,
      '',
      'ListRoutes',
      body
    );

    const domains: DomainInfo[] = [];
    if (response && typeof response === 'object') {
      const result = response.Result || {};
      const routes = result.Items || [];

      for (const route of routes) {
        // Derive path prefix from match rule
        let pathPrefix = '';
        try {
          const matchRule = route.MatchRule || {};
          const pathRule = matchRule.Path || {};
          const matchContent = pathRule.MatchContent;
          if (typeof matchContent === 'string') {
            pathPrefix = matchContent;
          }
        } catch (error) {
          pathPrefix = '';
        }

        const routeDomains = route.Domains || [];
        for (const domainInfo of routeDomains) {
          const base = domainInfo.Domain;
          if (!base) {
            continue;
          }
          domains.push({
            domain: `${base}${pathPrefix}`,
            type: domainInfo.Type || domainInfo.type,
          });
        }
      }
    }

    return domains;
  }

  /**
   * Get domains for APIG triggers of a given function.
   *
   * @param functionId - The function ID to get domains for
   * @returns List of domains from APIG routes, or empty list
   */
  async getApigDomains(functionId: string): Promise<DomainInfo[]> {
    const upstreamId = await this.getApigTrigger(functionId);
    if (upstreamId) {
      return this.getApigDomainsFromUpstream(upstreamId);
    }
    return [];
  }

  /**
   * Create an application using Volcengine VEFAAS.
   *
   * @param name - Application name
   * @param gatewayName - Gateway name
   * @param kwargs - Additional parameters
   * @returns Application ID or null
   */
  private async createApplicationInternal(name: string, gatewayName: string, ...kwargs: any[]): Promise<string | null> {
    const functionName = `${name}-function`;
    const sid = Math.random().toString().slice(2, 9);

    const body = JSON.stringify({
      Name: name,
      Config: {
        region: 'cn-beijing',
        functionName,
        gatewayName,
        sid,
      },
      TemplateId: '68ad2fb0443cb8000843cbbe',
    });

    try {
      const response = await request(
        'POST',
        new Date(),
        {},
        {},
        this.accessKey,
        this.secretKey,
        '',
        'CreateApplication',
        body
      );

      if (typeof response !== 'object' || !response) {
        console.error('CreateApplication returned non-object response:', response);
        return null;
      }

      const result = response.Result;
      if (typeof result !== 'object' || !result) {
        console.error('CreateApplication response missing Result:', response);
        return null;
      }

      const applicationId = result.Id;
      if (!applicationId) {
        console.error('CreateApplication response missing Result.Id:', response);
        return null;
      }

      return applicationId;
    } catch (error) {
      console.error('CreateApplication request failed:', error);
      return null;
    }
  }

  /**
   * Release an application using Volcengine VEFAAS.
   *
   * @param id - Application ID
   * @param kwargs - Additional parameters
   * @returns Response from the API
   */
  private async releaseApplication(id: string, ...kwargs: any[]): Promise<any> {
    const body = JSON.stringify({ Id: id });

    const response = await request(
      'POST',
      new Date(),
      {},
      {},
      this.accessKey,
      this.secretKey,
      '',
      'ReleaseApplication',
      body
    );

    return response;
  }

  /**
   * Create an application using Volcengine VEFAAS.
   *
   * @param name - Application name
   * @param gatewayName - Gateway name
   * @param kwargs - Additional parameters
   * @returns Application ID or null
   */
  async createApplication(name: string, gatewayName: string, ...kwargs: any[]): Promise<string | null> {
    if (!name) {
      throw new Error('name is required to create an application');
    }
    if (!gatewayName) {
      throw new Error('gateway_name is required to create an application');
    }

    const applicationId = await this.createApplicationInternal(name, gatewayName, ...kwargs);
    if (!applicationId) {
      return null;
    }

    try {
      await this.releaseApplication(applicationId, ...kwargs);
    } catch (error) {
      console.error(`ReleaseApplication request failed for id ${applicationId}:`, error);
    }

    return applicationId;
  }

  /**
   * Return readiness flag and function ID when available.
   *
   * @param id - Application ID
   * @param kwargs - Additional parameters
   * @returns Tuple of [isReady, functionId]
   */
  async getApplicationReadiness(id: string, ...kwargs: any[]): Promise<[boolean, string | null]> {
    const body = JSON.stringify({ Id: id });

    try {
      const response = await request(
        'POST',
        new Date(),
        {},
        {},
        this.accessKey,
        this.secretKey,
        '',
        'GetApplication',
        body
      );

      if (typeof response !== 'object' || !response) {
        console.error('GetApplication returned non-object response:', response);
        return [false, null];
      }

      const result = response.Result;
      if (typeof result !== 'object' || !result) {
        console.error('GetApplication response missing Result:', response);
        return [false, null];
      }

      let functionId: string | null = null;
      const cloudResourceRaw = result.CloudResource;

      if (typeof cloudResourceRaw === 'string') {
        try {
          const cloudResource = JSON.parse(cloudResourceRaw);
          if (typeof cloudResource === 'object') {
            functionId = cloudResource.function_id;
            if (!functionId) {
              const sandboxInfo = cloudResource.sandbox;
              if (typeof sandboxInfo === 'object') {
                functionId = sandboxInfo.function_id;
              }
            }
          }
        } catch (error) {
          console.error(`Failed to decode CloudResource for application ${id}:`, error);
        }
      } else if (typeof cloudResourceRaw === 'object') {
        functionId = cloudResourceRaw.function_id;
      }

      const status = result.Status;
      const isReady = status === 'deploy_success';

      if (!isReady) {
        console.log(`Application ${id} not ready. Status: ${status}`);
        return [false, functionId];
      }

      return [true, functionId];
    } catch (error) {
      console.error(`GetApplication request failed for id ${id}:`, error);
      return [false, null];
    }
  }
}
