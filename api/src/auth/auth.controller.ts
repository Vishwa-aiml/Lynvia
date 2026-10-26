import {
  Controller,
  Post,
  Body,
  Get,
  UseGuards,
  ConflictException,
  BadRequestException,
} from '@nestjs/common';
import { FirebaseAuthGuard } from './firebase-auth.guard';
import { CurrentUser } from './current-user.decorator';
import { PrismaService } from '../prisma/prisma.service';
import { Role } from '@prisma/client';
import type { User } from '@prisma/client';
import { IsEnum, IsString, IsOptional, MaxLength } from 'class-validator';

class OnboardingDto {
  @IsEnum(['CLIENT', 'DESIGNER'], {
    message: 'role must be CLIENT or DESIGNER',
  })
  role: 'CLIENT' | 'DESIGNER';

  @IsString()
  @MaxLength(100)
  name: string;

  @IsOptional()
  @IsString()
  @MaxLength(500)
  bio?: string;
}

/**
 * Auth Controller
 *
 * GET  /api/auth/me          — returns current user from DB (upserted by FirebaseAuthGuard)
 * POST /api/auth/onboarding  — assigns role, creates profile
 *
 * No webhook endpoint needed — user is created lazily on first /auth/me call.
 * Role is set SERVER-SIDE only. ADMIN is never self-assignable.
 */
@Controller('auth')
export class AuthController {
  constructor(private prisma: PrismaService) {}

  /**
   * Returns the current user's profile.
   * User is guaranteed to exist in DB — FirebaseAuthGuard upserts it on every request.
   */
  @Get('me')
  @UseGuards(FirebaseAuthGuard)
  async getMe(@CurrentUser() user: User) {
    const [clientProfile, designerProfile] = await Promise.all([
      user.role === 'CLIENT'
        ? this.prisma.clientProfile.findUnique({ where: { userId: user.id } })
        : null,
      user.role === 'DESIGNER'
        ? this.prisma.designerProfile.findUnique({ where: { userId: user.id } })
        : null,
    ]);

    return {
      id: user.id,
      email: user.email,
      role: user.role,
      onboardingComplete: user.role !== null,
      profile: clientProfile ?? designerProfile ?? null,
    };
  }

  /**
   * Onboarding — sets role and creates profile.
   * Called exactly once per user after Firebase sign-up.
   * ADMIN role is NEVER self-assignable.
   */
  @Post('onboarding')
  @UseGuards(FirebaseAuthGuard)
  async onboard(
    @CurrentUser() user: User,
    @Body() dto: OnboardingDto,
  ) {
    if (user.role !== null) {
      throw new ConflictException('Onboarding already complete');
    }

    if ((dto.role as string) === 'ADMIN') {
      throw new BadRequestException('Invalid role');
    }

    const role = dto.role as Role;

    if (role === Role.CLIENT) {
      await this.prisma.$transaction([
        this.prisma.user.update({
          where: { id: user.id },
          data: { role: Role.CLIENT },
        }),
        this.prisma.clientProfile.create({
          data: {
            userId: user.id,
            name: dto.name,
            bio: dto.bio,
          },
        }),
      ]);
    } else if (role === Role.DESIGNER) {
      await this.prisma.$transaction([
        this.prisma.user.update({
          where: { id: user.id },
          data: { role: Role.DESIGNER },
        }),
        this.prisma.designerProfile.create({
          data: {
            userId: user.id,
            name: dto.name,
            bio: dto.bio,
            portfolioUrls: [],
            specializations: [],
            vettingStatus: 'PENDING',
          },
        }),
      ]);
    }

    return { success: true, role };
  }
}
