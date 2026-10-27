import { createParamDecorator, ExecutionContext } from '@nestjs/common';
import { User } from '@prisma/client';

/**
 * Extracts the authenticated DB user from request.
 * req.user is set by authentication guard after DB lookup.
 *
 * Example:
 *   @Get('me')
 *   @UseGuards(FirebaseAuthGuard)
 *   getMe(@CurrentUser() user: User) { ... }
 */
export const CurrentUser = createParamDecorator(
  (_data: unknown, ctx: ExecutionContext): User => {
    const request = ctx.switchToHttp().getRequest();
    return request.user as User;
  },
);
