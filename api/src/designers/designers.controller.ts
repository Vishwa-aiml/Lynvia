import {
  Controller,
  Get,
  Post,
  Patch,
  Param,
  Body,
  UseGuards,
} from '@nestjs/common';
import { FirebaseAuthGuard } from '../auth/firebase-auth.guard';
import { CurrentUser } from '../auth/current-user.decorator';
import { Roles } from '../auth/roles.decorator';
import { DesignersService } from './designers.service';
import { User } from '@prisma/client';
import { IsString, IsEnum, IsOptional, MaxLength } from 'class-validator';

class PortfolioUploadRequestDto {
  @IsString()
  @MaxLength(255)
  filename: string;

  @IsEnum(['image/jpeg', 'image/png', 'image/webp'], {
    message: 'Only image/jpeg, image/png, and image/webp are allowed',
  })
  contentType: string;
}

class PortfolioConfirmDto {
  @IsString()
  @MaxLength(500)
  s3Key: string;
}

class VettingDto {
  @IsEnum(['APPROVED', 'REJECTED']) status: 'APPROVED' | 'REJECTED';
  @IsOptional() @IsString() @MaxLength(1000) note?: string;
}

@Controller('designers')
export class DesignersController {
  constructor(private designers: DesignersService) {}

  /** Public: list approved designers (no auth required) */
  @Get()
  findAll() {
    return this.designers.findApproved();
  }

  /** Public: view a designer's profile */
  @Get(':userId')
  findOne(@Param('userId') userId: string) {
    return this.designers.findOne(userId);
  }

  /** Public: get signed portfolio URLs for a designer */
  @Get(':userId/portfolio')
  @UseGuards(FirebaseAuthGuard)
  getPortfolio(
    @Param('userId') userId: string,
    @CurrentUser() user: User,
  ) {
    return this.designers.getPortfolioSignedUrls(userId, user.id);
  }

  /** DESIGNER: get a pre-signed upload URL for a portfolio image */
  @Post('portfolio/upload-url')
  @UseGuards(FirebaseAuthGuard)
  @Roles('DESIGNER' as any)
  getUploadUrl(
    @CurrentUser() user: User,
    @Body() dto: PortfolioUploadRequestDto,
  ) {
    return this.designers.getPortfolioUploadUrl(
      user,
      dto.filename,
      dto.contentType,
    );
  }

  /** DESIGNER: confirm portfolio item after upload */
  @Post('portfolio/confirm')
  @UseGuards(FirebaseAuthGuard)
  @Roles('DESIGNER' as any)
  confirmUpload(
    @CurrentUser() user: User,
    @Body() dto: PortfolioConfirmDto,
  ) {
    return this.designers.addPortfolioItem(user, dto.s3Key);
  }

  // ─── Admin routes ──────────────────────────────────────────────────────────

  /** ADMIN: view pending designer applications */
  @Get('admin/pending')
  @UseGuards(FirebaseAuthGuard)
  @Roles('ADMIN' as any)
  getPending() {
    return this.designers.getPendingDesigners();
  }

  /** ADMIN: approve or reject a designer */
  @Patch('admin/:userId/vetting')
  @UseGuards(FirebaseAuthGuard)
  @Roles('ADMIN' as any)
  updateVetting(
    @Param('userId') userId: string,
    @Body() dto: VettingDto,
  ) {
    return this.designers.updateVettingStatus(userId, dto.status, dto.note);
  }
}
