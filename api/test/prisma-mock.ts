import { vi } from 'vitest';

export type MockPrismaService = {
  $connect: ReturnType<typeof vi.fn>;
  $disconnect: ReturnType<typeof vi.fn>;
  $transaction: ReturnType<typeof vi.fn>;
  user: Record<string, ReturnType<typeof vi.fn>>;
  clientProfile: Record<string, ReturnType<typeof vi.fn>>;
  designerProfile: Record<string, ReturnType<typeof vi.fn>>;
  project: Record<string, ReturnType<typeof vi.fn>>;
  proposal: Record<string, ReturnType<typeof vi.fn>>;
};

export function createMockPrismaService(): MockPrismaService {
  return {
    $connect: vi.fn().mockResolvedValue(undefined),
    $disconnect: vi.fn().mockResolvedValue(undefined),
    $transaction: vi.fn().mockImplementation((arg: any) => {
      if (typeof arg === 'function') {
        return arg(createMockPrismaService());
      }
      return Promise.all(arg);
    }),
    user: {
      findUnique: vi.fn(),
      findFirst: vi.fn(),
      findMany: vi.fn(),
      create: vi.fn(),
      update: vi.fn(),
      upsert: vi.fn(),
      delete: vi.fn(),
    },
    clientProfile: {
      findUnique: vi.fn(),
      findFirst: vi.fn(),
      findMany: vi.fn(),
      create: vi.fn(),
      update: vi.fn(),
      delete: vi.fn(),
    },
    designerProfile: {
      findUnique: vi.fn(),
      findFirst: vi.fn(),
      findMany: vi.fn(),
      create: vi.fn(),
      update: vi.fn(),
      delete: vi.fn(),
    },
    project: {
      findUnique: vi.fn(),
      findFirst: vi.fn(),
      findMany: vi.fn(),
      create: vi.fn(),
      update: vi.fn(),
      delete: vi.fn(),
    },
    proposal: {
      findUnique: vi.fn(),
      findFirst: vi.fn(),
      findMany: vi.fn(),
      create: vi.fn(),
      update: vi.fn(),
      updateMany: vi.fn(),
      delete: vi.fn(),
    },
  };
}
