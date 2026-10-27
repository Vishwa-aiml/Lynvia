import { describe, it, expect, beforeEach } from 'vitest';
import { DesignersService } from './designers.service';
import { createMockPrismaService, MockPrismaService } from '../../test/prisma-mock';
import { ForbiddenException, NotFoundException } from '@nestjs/common';
import { Role, User, VettingStatus } from '@prisma/client';

describe('DesignersService', () => {
  let service: DesignersService;
  let mockPrisma: MockPrismaService;
  let mockStorage: {
    portfolioKey: (userId: string, filename: string) => string;
    getUploadUrl: (key: string, contentType: string) => Promise<{ uploadUrl: string; key: string }>;
  };

  const mockDesignerUser: User = {
    id: 'des_123',
    firebaseUid: 'fb_123',
    email: 'designer@example.com',
    role: Role.DESIGNER,
    createdAt: new Date(),
    updatedAt: new Date(),
  };

  beforeEach(() => {
    mockPrisma = createMockPrismaService();
    mockStorage = {
      portfolioKey: (userId: string, filename: string) => `portfolios/${userId}/12345-${filename}`,
      getUploadUrl: async (key: string) => ({
        uploadUrl: `https://s3.example.com/${key}`,
        key,
      }),
    };

    service = new DesignersService(mockPrisma as any, mockStorage as any);
  });

  describe('findApproved', () => {
    it('queries only designers with vettingStatus APPROVED', async () => {
      mockPrisma.designerProfile.findMany.mockResolvedValue([
        { id: 'dp_1', userId: 'des_123', vettingStatus: VettingStatus.APPROVED },
      ]);

      const result = await service.findApproved();

      expect(mockPrisma.designerProfile.findMany).toHaveBeenCalledWith({
        where: { vettingStatus: 'APPROVED' },
        include: { user: { select: { id: true } } },
        orderBy: { createdAt: 'desc' },
      });
      expect(result).toHaveLength(1);
    });
  });

  describe('findOne', () => {
    it('throws NotFoundException when profile does not exist', async () => {
      mockPrisma.designerProfile.findUnique.mockResolvedValue(null);

      await expect(service.findOne('non_existent')).rejects.toThrow(NotFoundException);
    });

    it('throws NotFoundException when vettingStatus is not APPROVED', async () => {
      mockPrisma.designerProfile.findUnique.mockResolvedValue({
        id: 'dp_2',
        userId: 'des_456',
        vettingStatus: VettingStatus.PENDING,
      });

      await expect(service.findOne('des_456')).rejects.toThrow(NotFoundException);
    });

    it('returns profile when vettingStatus is APPROVED', async () => {
      mockPrisma.designerProfile.findUnique.mockResolvedValue({
        id: 'dp_1',
        userId: 'des_123',
        vettingStatus: VettingStatus.APPROVED,
      });

      const profile = await service.findOne('des_123');
      expect(profile.id).toBe('dp_1');
    });
  });

  describe('addPortfolioItem', () => {
    it('throws ForbiddenException if s3Key does not start with portfolios/{designer.id}/', async () => {
      await expect(
        service.addPortfolioItem(mockDesignerUser, 'portfolios/other_user/bad_file.png'),
      ).rejects.toThrow(ForbiddenException);
    });

    it('appends s3Key to portfolioUrls and saves to DB', async () => {
      mockPrisma.designerProfile.findUnique.mockResolvedValue({
        id: 'dp_1',
        userId: 'des_123',
        portfolioUrls: ['portfolios/des_123/existing.png'],
      });
      mockPrisma.designerProfile.update.mockResolvedValue({
        id: 'dp_1',
        userId: 'des_123',
        portfolioUrls: ['portfolios/des_123/existing.png', 'portfolios/des_123/new.png'],
      });

      const updated = await service.addPortfolioItem(
        mockDesignerUser,
        'portfolios/des_123/new.png',
      );

      expect(mockPrisma.designerProfile.update).toHaveBeenCalledWith({
        where: { userId: 'des_123' },
        data: {
          portfolioUrls: ['portfolios/des_123/existing.png', 'portfolios/des_123/new.png'],
        },
      });
      expect(updated.portfolioUrls).toHaveLength(2);
    });
  });
});
