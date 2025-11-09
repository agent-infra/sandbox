import { SandboxClient } from '@agent-infra/sandbox';

const client = new SandboxClient({
  environment: process.env.SANDBOX_API_URL || 'http://localhost:8080',
  timeoutInSeconds: 5, // 5 second timeout
});

/**
 * Demonstrates handling different types of errors
 */
async function handleSpecificErrors() {
  console.log('=== Error Handling Examples ===\n');

  try {
    // This will likely fail if sandbox is not running
    const response = await client.sandbox.getContext();

    if (!response.ok) {
      console.error('🚨 API Error Response:');
      console.error('  Status:', response.rawResponse.status);
    }
  } catch (error) {
    if (error instanceof Error) {
      console.error('❌ Error:');
      console.error(`   Message: ${error.message}`);
      console.error(`   Name: ${error.name}`);
      console.error(`   Suggestion: Check API configuration or connectivity\n`);
    } else {
      console.error('❌ Unknown Error:', error, '\n');
    }
  }
}

/**
 * Retry function with exponential backoff
 */
async function retryWithBackoff<T>(
  fn: () => Promise<T>,
  options: {
    maxRetries?: number;
    initialDelay?: number;
    maxDelay?: number;
    backoffMultiplier?: number;
  } = {},
): Promise<T> {
  const {
    maxRetries = 3,
    initialDelay = 1000,
    maxDelay = 10000,
    backoffMultiplier = 2,
  } = options;

  let lastError: Error;

  for (let attempt = 0; attempt < maxRetries; attempt++) {
    try {
      return await fn();
    } catch (error) {
      lastError = error instanceof Error ? error : new Error(String(error));

      // Don't retry on certain error types (e.g., authentication errors)
      if (error instanceof Error && error.message.includes('401')) {
        throw new Error('Authentication failed - not retrying');
      }

      if (attempt === maxRetries - 1) {
        break; // Last attempt, throw error
      }

      const delay = Math.min(
        initialDelay * Math.pow(backoffMultiplier, attempt),
        maxDelay,
      );

      console.log(
        `   Attempt ${attempt + 1}/${maxRetries} failed. ` +
          `Retrying in ${delay}ms...`,
      );

      await new Promise((resolve) => setTimeout(resolve, delay));
    }
  }

  throw lastError!;
}

/**
 * Circuit breaker pattern for handling repeated failures
 */
class CircuitBreaker {
  private failureCount = 0;
  private lastFailureTime = 0;
  private state: 'CLOSED' | 'OPEN' | 'HALF_OPEN' = 'CLOSED';

  constructor(
    private readonly threshold: number = 5,
    private readonly timeout: number = 60000, // 60 seconds
  ) {}

  async execute<T>(fn: () => Promise<T>): Promise<T> {
    if (this.state === 'OPEN') {
      if (Date.now() - this.lastFailureTime > this.timeout) {
        this.state = 'HALF_OPEN';
        console.log('🔄 Circuit breaker: Attempting recovery (HALF_OPEN)');
      } else {
        throw new Error('Circuit breaker is OPEN - too many failures');
      }
    }

    try {
      const result = await fn();

      if (this.state === 'HALF_OPEN') {
        console.log('✓ Circuit breaker: Recovery successful (CLOSED)');
        this.state = 'CLOSED';
        this.failureCount = 0;
      }

      return result;
    } catch (error) {
      this.failureCount++;
      this.lastFailureTime = Date.now();

      if (this.failureCount >= this.threshold) {
        this.state = 'OPEN';
        console.error(
          `🔌 Circuit breaker: OPEN (${this.failureCount} failures)`,
        );
      }

      throw error;
    }
  }

  getState() {
    return {
      state: this.state,
      failureCount: this.failureCount,
      lastFailureTime: this.lastFailureTime,
    };
  }
}

/**
 * Demonstrates retry logic with exponential backoff
 */
async function demonstrateRetry() {
  console.log('\n=== Retry with Exponential Backoff ===\n');

  try {
    const result = await retryWithBackoff(
      async () => {
        console.log('   Attempting shell command...');
        const response = await client.shell.execCommand({
          command: 'echo "Hello from retry"',
        });

        if (!response.ok) {
          throw new Error('Command failed');
        }

        return response.body;
      },
      {
        maxRetries: 3,
        initialDelay: 1000,
        backoffMultiplier: 2,
      },
    );

    console.log('✓ Success:', result.data, '\n');
  } catch (error) {
    console.error(
      '❌ All retries exhausted:',
      error instanceof Error ? error.message : error,
      '\n',
    );
  }
}

/**
 * Demonstrates circuit breaker pattern
 */
async function demonstrateCircuitBreaker() {
  console.log('=== Circuit Breaker Pattern ===\n');

  const breaker = new CircuitBreaker(3, 5000); // 3 failures, 5 second timeout

  for (let i = 0; i < 6; i++) {
    try {
      await breaker.execute(async () => {
        console.log(`   Request ${i + 1}...`);

        // Simulate failures for first 4 requests
        if (i < 4) {
          throw new Error('Simulated failure');
        }

        return { success: true };
      });

      console.log(`✓ Request ${i + 1} succeeded`);
    } catch (error) {
      console.error(
        `❌ Request ${i + 1} failed:`,
        error instanceof Error ? error.message : error,
      );
    }

    console.log('   State:', breaker.getState(), '\n');
  }
}

/**
 * Graceful degradation example
 */
async function gracefulDegradation() {
  console.log('=== Graceful Degradation ===\n');

  try {
    const response = await client.sandbox.getPythonPackages();

    if (response.ok) {
      console.log(`✓ Package info retrieved successfully\n`);
    } else {
      throw new Error('Failed to fetch packages');
    }
  } catch (error) {
    console.warn('⚠️  Could not fetch packages, using cached data');
    console.warn('   Error:', error instanceof Error ? error.message : error);

    // Fallback to cached or default data
    const cachedPackages: string[] = []; // Load from cache
    console.log(`✓ Using ${cachedPackages.length} cached packages\n`);
  }
}

async function main() {
  await handleSpecificErrors();
  await demonstrateRetry();
  await demonstrateCircuitBreaker();
  await gracefulDegradation();
}

main();
