import {
  Injectable,
  CanActivate,
  ExecutionContext,
  UnauthorizedException,
  ForbiddenException,
  OnModuleInit,
} from '@nestjs/common';
import { Reflector } from '@nestjs/core';
import { initializeApp, getApps, App, cert } from 'firebase-admin/app';
import { getAuth, DecodedIdToken } from 'firebase-admin/auth';
import { PrismaService } from '../prisma/prisma.service';
import { Role, User } from '@prisma/client';
import { ROLES_KEY } from './roles.decorator';

/**
 * Combined Firebase auth + RBAC guard.
 *
 * Usage:
 *   @UseGuards(FirebaseAuthGuard)                 — any authenticated user
 *   @Roles(Role.CLIENT)  @UseGuards(FirebaseAuthGuard)  — only CLIENTs
 *   @Roles(Role.ADMIN)   @UseGuards(FirebaseAuthGuard)  — only ADMINs
 *
 * What this does:
 *  1. Extracts Bearer token from Authorization header
 *  2. Verifies it with firebase-admin getAuth().verifyIdToken()
 *  3. Upserts the user into our DB (lazy creation on first request — no webhook needed)
 *  4. Attaches the full DB User object to request.user
 *  5. Enforces RBAC if @Roles() is present
 *
 * Role is always read from DB — NEVER from the Firebase token.
 */
@Injectable()
export class FirebaseAuthGuard implements CanActivate, OnModuleInit {
  private app!: App;

  constructor(
    private reflector: Reflector,
    private prisma: PrismaService,
  ) {}

  onModuleInit() {
    // Initialize Firebase Admin once — idempotent
    if (getApps().length === 0) {
      this.app = initializeApp({
        credential: cert({
          projectId: process.env.FIREBASE_PROJECT_ID,
          clientEmail: process.env.FIREBASE_CLIENT_EMAIL,
          // Replace escaped newlines from env var string
          privateKey: (process.env.FIREBASE_PRIVATE_KEY ?? '').replace(/\\n/g, '\n'),
        }),
      });
    } else {
      this.app = getApps()[0];
    }
  }

  async canActivate(context: ExecutionContext): Promise<boolean> {
    const request = context.switchToHttp().getRequest<{
      headers: Record<string, string>;
      user: User;
    }>();

    // 1. Extract token
    const authHeader = request.headers['authorization'] ?? '';
    if (!authHeader.startsWith('Bearer ')) {
      throw new UnauthorizedException('Missing or malformed Authorization header');
    }
    const token = authHeader.slice(7);

    // 2. Verify with Firebase Admin
    let decoded: DecodedIdToken;
    try {
      decoded = await getAuth(this.app).verifyIdToken(token);
    } catch {
      throw new UnauthorizedException('Invalid or expired Firebase token');
    }

    const firebaseUid = decoded.uid;
    const email = decoded.email ?? '';

    // 3. Upsert user in DB — creates record on first call, or links existing account
    let user = await this.prisma.user.findUnique({ where: { firebaseUid } });

    if (!user) {
      const existingByEmail = email
        ? await this.prisma.user.findUnique({ where: { email } })
        : null;

      if (existingByEmail) {
        user = await this.prisma.user.update({
          where: { id: existingByEmail.id },
          data: { firebaseUid },
        });
      } else {
        user = await this.prisma.user.create({
          data: {
            firebaseUid,
            email,
            role: null, // set during onboarding
          },
        });
      }
    }

    // 4. Attach DB user to request
    request.user = user;

    // 5. RBAC
    const requiredRoles = this.reflector.getAllAndOverride<Role[]>(ROLES_KEY, [
      context.getHandler(),
      context.getClass(),
    ]);

    if (!requiredRoles || requiredRoles.length === 0) {
      return true; // no role restriction
    }

    if (!user.role || !requiredRoles.includes(user.role)) {
      throw new ForbiddenException(
        `Access denied — requires role: ${requiredRoles.join(' or ')}`,
      );
    }

    return true;
  }
}
