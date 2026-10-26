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
import { ProjectsService } from './projects.service';
import { CreateProjectDto } from './dto/create-project.dto';
import { User } from '@prisma/client';

@Controller('projects')
@UseGuards(FirebaseAuthGuard)
export class ProjectsController {
  constructor(private projects: ProjectsService) {}

  /** CLIENT: create a new project */
  @Post()
  @Roles('CLIENT' as any)
  create(@CurrentUser() user: User, @Body() dto: CreateProjectDto) {
    return this.projects.create(user, dto);
  }

  /** ANY authenticated user: browse open projects */
  @Get()
  findAllOpen() {
    return this.projects.findAllOpen();
  }

  /** CLIENT: view their own projects */
  @Get('mine')
  @Roles('CLIENT' as any)
  findMine(@CurrentUser() user: User) {
    return this.projects.findMyProjects(user);
  }

  /** Any participant: view a specific project */
  @Get(':id')
  findOne(@Param('id') id: string, @CurrentUser() user: User) {
    return this.projects.findOne(id, user.id, user.role ?? '');
  }

  /** CLIENT: accept a proposal — triggers state transition */
  @Patch(':id/accept-proposal/:proposalId')
  @Roles('CLIENT' as any)
  acceptProposal(
    @Param('id') id: string,
    @Param('proposalId') proposalId: string,
    @CurrentUser() user: User,
  ) {
    return this.projects.acceptProposal(id, proposalId, user.id);
  }
}
