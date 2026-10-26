import { Injectable, NotFoundException, ForbiddenException } from '@nestjs/common';
import { PrismaService } from '../prisma/prisma.service';
import { StorageService } from '../storage/storage.service';
import { User } from '@prisma/client';

@Injectable()
export class DesignersService {
  constructor(
    private prisma: PrismaService,
    private storage: StorageService,
  ) {}

  /** Public listing — ONLY approved designers */
  async findApproved() {
    return this.prisma.designerProfile.findMany({
      where: { vettingStatus: 'APPROVED' },
      include: {
        user: { select: { id: true } },
      },
      orderBy: { createdAt: 'desc' },
    });
  }

  /** Public profile — only approved designers are viewable publicly */
  async findOne(userId: string) {
    const profile = await this.prisma.designerProfile.findUnique({
      where: { userId },
      include: { user: { select: { id: true, email: true } } },
    });

    if (!profile) throw new NotFoundException('Designer not found');
    if (profile.vettingStatus !== 'APPROVED') {
      throw new NotFoundException('Designer not found');
    }

    return profile;
  }

  /** Designer: get upload URL for portfolio image */
  async getPortfolioUploadUrl(
    designer: User,
    filename: string,
    contentType: string,
  ) {
    const key = this.storage.portfolioKey(designer.id, filename);
    return this.storage.getUploadUrl(key, contentType);
  }

  /** Designer: add a portfolio image key to their profile (after upload) */
  async addPortfolioItem(designer: User, s3Key: string) {
    // Security check: verify that s3Key belongs to this designer's portfolio namespace
    if (!s3Key.startsWith(`portfolios/${designer.id}/`)) {
      throw new ForbiddenException('Invalid S3 key: key must belong to your portfolio namespace');
    }

    const profile = await this.prisma.designerProfile.findUnique({
      where: { userId: designer.id },
    });
    if (!profile) throw new NotFoundException('Profile not found');

    return this.prisma.designerProfile.update({
      where: { userId: designer.id },
      data: {
        portfolioUrls: [...profile.portfolioUrls, s3Key],
      },
    });
  }

  /** Get signed URLs for portfolio items (called after ownership check) */
  async getPortfolioSignedUrls(userId: string, requesterId: string) {
    const profile = await this.prisma.designerProfile.findUnique({
      where: { userId },
    });
    if (!profile) throw new NotFoundException('Profile not found');

    // Public profiles: only approved designers' portfolios are viewable
    const isOwner = userId === requesterId;
    if (!isOwner && profile.vettingStatus !== 'APPROVED') {
      throw new ForbiddenException('Profile not publicly viewable');
    }

    const urls = await Promise.all(
      profile.portfolioUrls.map((key) =>
        this.storage.getSignedUrl(key, 'preview'),
      ),
    );

    return { items: profile.portfolioUrls.map((key, i) => ({ key, url: urls[i] })) };
  }

  // ─── Admin-only ───────────────────────────────────────────────────────────

  async getPendingDesigners() {
    return this.prisma.designerProfile.findMany({
      where: { vettingStatus: 'PENDING' },
      include: { user: { select: { id: true, email: true } } },
      orderBy: { createdAt: 'asc' },
    });
  }

  async updateVettingStatus(
    designerUserId: string,
    status: 'APPROVED' | 'REJECTED',
    note?: string,
  ) {
    const profile = await this.prisma.designerProfile.findUnique({
      where: { userId: designerUserId },
    });
    if (!profile) throw new NotFoundException('Designer profile not found');

    return this.prisma.designerProfile.update({
      where: { userId: designerUserId },
      data: {
        vettingStatus: status,
        vettingNote: note,
      },
    });
  }
}
