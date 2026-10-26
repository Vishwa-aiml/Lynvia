import { Controller, Get, Post, Body, Param, UseGuards } from '@nestjs/common';
import { FirebaseAuthGuard } from '../auth/firebase-auth.guard';
import { CurrentUser } from '../auth/current-user.decorator';
import { Roles } from '../auth/roles.decorator';
import { ProposalsService } from './proposals.service';
import { CreateProposalDto } from './dto/create-proposal.dto';
import { User } from '@prisma/client';

@Controller('proposals')
@UseGuards(FirebaseAuthGuard)
export class ProposalsController {
  constructor(private proposals: ProposalsService) {}

  /** DESIGNER: submit a proposal */
  @Post()
  @Roles('DESIGNER' as any)
  create(@CurrentUser() user: User, @Body() dto: CreateProposalDto) {
    return this.proposals.create(user, dto);
  }

  /** DESIGNER: view all their proposals */
  @Get('mine')
  @Roles('DESIGNER' as any)
  findMine(@CurrentUser() user: User) {
    return this.proposals.findMyProposals(user);
  }

  /** CLIENT: view proposals for a specific project */
  @Get('for-project/:projectId')
  @Roles('CLIENT' as any)
  findForProject(
    @Param('projectId') projectId: string,
    @CurrentUser() user: User,
  ) {
    return this.proposals.findForProject(projectId, user.id);
  }
}
