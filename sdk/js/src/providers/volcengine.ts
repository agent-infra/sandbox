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
   * @param timeout - The timeout for the sandbox creation in seconds (default: 60)
   * @param kwargs - Additional parameters for sandbox creation
   * @returns The ID of the created sandbox or error
   */
  async createSandbox(
    functionId: string,
    timeout: number = 60,
    ...kwargs: any[]
  ): Promise<any> {
    try {
      const params = kwargs[0] || {};
      const body = JSON.stringify({
        FunctionId: functionId,
        Timeout: timeout,
        Metadata: params.metadata,
        InstanceTosMountConfig: params.instanceTosMountConfig,
        Envs: params.envs,
        InstanceImageInfo: params.instanceImageInfo,
        CpuMilli: params.cpuMilli,
        MemoryMB: params.memoryMB,
        MaxConcurrency: params.maxConcurrency,
        RequestTimeout: params.requestTimeout,
        ...kwargs[0]
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
        body,
      );

      return response;
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
  async deleteSandbox(
    functionId: string,
    sandboxId: string,
    ...kwargs: any[]
  ): Promise<any> {
    try {
      const body = JSON.stringify({
        FunctionId: functionId,
        SandboxId: sandboxId,
        ...kwargs[0]
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
        body,
      );

      return response;
    } catch (error) {
      return error;
    }
  }

  /**
   * Append ?faasInstanceName= to domain field of structured domain objects.
   */
  private appendInstanceQueryStruct(
    domainsInfo: DomainInfo[],
    instanceName: string,
  ): DomainInfo[] {
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
  async getSandbox(
    functionId: string,
    sandboxId: string,
    ...kwargs: any[]
  ): Promise<any> {
    try {
      const body = JSON.stringify({
        SandboxId: sandboxId,
        FunctionId: functionId,
        ...kwargs[0]
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
        body,
      );

      if (response?.Result) {
        const baseDomains = await this.getApigDomains(functionId);
        const domainsStruct = this.appendInstanceQueryStruct(
          baseDomains,
          sandboxId,
        );
        response.Result.domains = domainsStruct;
      }

      return response;
    } catch (error) {
      return error;
    }
  }

  /**
   * Set the timeout for an existing sandbox instance.
   *
   * @param functionId - The function ID of the sandbox
   * @param sandboxId - The ID of the sandbox to update
   * @param timeout - The new timeout value in seconds
   * @param kwargs - Additional parameters
   * @returns The response containing the updated sandbox information
   */
  async setSandboxTimeout(
    functionId: string,
    sandboxId: string,
    timeout: number,
  ): Promise<any> {
    try {
      const body = JSON.stringify({
        FunctionId: functionId,
        SandboxId: sandboxId,
        Timeout: timeout,
      });

      const response = await request(
        'POST',
        new Date(),
        {},
        {},
        this.accessKey,
        this.secretKey,
        null,
        'SetSandboxTimeout',
        body,
      );

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
      const params = kwargs[0] || {};
      const body = JSON.stringify({
        FunctionId: functionId,
        SandboxId: params.sandboxId,
        Metadata: params.metadata,
        PageNumber: params.pageNumber || 1,
        PageSize: params.pageSize || 10,
        ImageUrl: params.imageUrl,
        Status: params.status,
        ...kwargs[0]
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
        body,
      );

      if (response?.Result) {
        const baseDomains = await this.getApigDomains(functionId);
        const sandboxes = response.Result.Sandboxes || [];
        const normalized: any[] = [];

        for (const sb of sandboxes) {
          const instanceId = sb.Id || sb.SandboxId;
          const domainsStruct = instanceId
            ? this.appendInstanceQueryStruct(baseDomains, instanceId)
            : baseDomains;
          sb.domains = domainsStruct;
          normalized.push(sb);
        }

        return {
          sandboxes: normalized,
          total: response.Result.Total,
          statusCount: response.Result.StatusCount,
        };
      }

      return response;
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
      body,
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
  private async getApigDomainsFromUpstream(
    upstreamId: string,
  ): Promise<DomainInfo[]> {
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
      body,
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
}
