import { Controller, Get, UseGuards } from '@nestjs/common';
import { FirebaseAuthGuard } from '../auth/firebase-auth.guard';
import { Roles } from '../auth/roles.decorator';
import { CurrentUser } from '../auth/current-user.decorator';
import { PrismaService } from '../prisma/prisma.service';
import { User } from '@prisma/client';

/**
 * Users Controller — minimal, admin-only user management.
 * Self-service profile is handled in AuthController (/auth/me)
 * and DesignersController.
 */
@Controller('users')
@UseGuards(FirebaseAuthGuard)
export class UsersController {
  constructor(private prisma: PrismaService) {}

  /** ADMIN: list all users */
  @Get()
  @Roles('ADMIN' as any)
  findAll() {
    return this.prisma.user.findMany({
      select: {
        id: true,
        email: true,
        role: true,
        createdAt: true,
        _count: {
          select: { projectsAsClient: true, proposals: true },
        },
      },
      orderBy: { createdAt: 'desc' },
    });
  }
}
