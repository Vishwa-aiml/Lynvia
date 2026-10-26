import { SetMetadata } from '@nestjs/common';
import { Role } from '@prisma/client';

export const ROLES_KEY = 'roles';

/**
 * Decorator to restrict an endpoint to specific roles.
 * Always pair with @UseGuards(ClerkAuthGuard).
 *
 * Example:
 *   @Roles(Role.ADMIN)
 *   @UseGuards(ClerkAuthGuard)
 *   @Get('admin/users')
 *   getUsers() { ... }
 */
export const Roles = (...roles: Role[]) => SetMetadata(ROLES_KEY, roles);
