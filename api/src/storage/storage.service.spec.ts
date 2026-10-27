import { describe, it, expect, vi, beforeEach } from 'vitest';
import { StorageService } from './storage.service';
import { ConfigService } from '@nestjs/config';

describe('StorageService', () => {
  let service: StorageService;
  let mockConfig: {
    getOrThrow: ReturnType<typeof vi.fn>;
    get: ReturnType<typeof vi.fn>;
  };

  beforeEach(() => {
    mockConfig = {
      getOrThrow: vi.fn((key: string) => {
        if (key === 'AWS_REGION') return 'ap-southeast-2';
        if (key === 'AWS_ACCESS_KEY_ID') return 'test-key-id';
        if (key === 'AWS_SECRET_ACCESS_KEY') return 'test-secret-key';
        if (key === 'AWS_S3_BUCKET_NAME') return 'lynvia-test-bucket';
        throw new Error(`Unexpected key: ${key}`);
      }),
      get: vi.fn((key: string) => {
        if (key === 'S3_PREVIEW_URL_TTL') return '900';
        if (key === 'S3_DELIVERY_URL_TTL') return '300';
        return undefined;
      }),
    };

    service = new StorageService(mockConfig as unknown as ConfigService);
  });

  describe('portfolioKey', () => {
    it('generates a structured key under portfolios/{userId}/ with sanitized filename', () => {
      const key = service.portfolioKey('user_123', 'My Portfolio #1 (Final).png');
      expect(key).toMatch(/^portfolios\/user_123\/\d+-My_Portfolio__1__Final_\.png$/);
    });

    it('preserves dots, dashes, and underscores in filename', () => {
      const key = service.portfolioKey('user_abc', 'banner-v2_final.jpg');
      expect(key).toMatch(/^portfolios\/user_abc\/\d+-banner-v2_final\.jpg$/);
    });
  });

  describe('deliveryKey', () => {
    it('generates a structured key under projects/{projectId}/delivery/ with sanitized filename', () => {
      const key = service.deliveryKey('proj_456', 'brand assets & logo.zip');
      expect(key).toMatch(/^projects\/proj_456\/delivery\/\d+-brand_assets___logo\.zip$/);
    });
  });
});
