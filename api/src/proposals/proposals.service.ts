import {
  Injectable,
  NotFoundException,
  ForbiddenException,
  ConflictException,
  BadRequestException,
} from '@nestjs/common';
import { PrismaService } from '../prisma/prisma.service';
import { User } from '@prisma/client';
import { CreateProposalDto } from './dto/create-proposal.dto';

/**
 * ProposalsService
 *
 * ALL proposal state transitions go through this service.
 * Status is NEVER set directly in a controller.
 */
@Injectable()
export class ProposalsService {
  constructor(private prisma: PrismaService) {}

  async create(designer: User, dto: CreateProposalDto) {
    // 1. Only APPROVED designers can submit proposals
    const profile = await this.prisma.designerProfile.findUnique({
      where: { userId: designer.id },
    });

    if (!profile || profile.vettingStatus !== 'APPROVED') {
      throw new ForbiddenException(
        'Only approved designers can submit proposals',
      );
    }

    // 2. Project must be OPEN
    const project = await this.prisma.project.findUnique({
      where: { id: dto.projectId },
    });

    if (!project) throw new NotFoundException('Project not found');
    if (project.status !== 'OPEN') {
      throw new ConflictException('Project is no longer accepting proposals');
    }

    // 3. Designer cannot bid on their own project (edge case)
    if (project.clientId === designer.id) {
      throw new BadRequestException('Cannot submit proposal on your own project');
    }

    // 4. One proposal per designer per project (enforced by DB unique index too)
    const existing = await this.prisma.proposal.findUnique({
      where: {
        projectId_designerId: {
          projectId: dto.projectId,
          designerId: designer.id,
        },
      },
    });

    if (existing) {
      throw new ConflictException('You have already submitted a proposal for this project');
    }

    return this.prisma.proposal.create({
      data: {
        projectId: dto.projectId,
        designerId: designer.id,
        bidPaise: dto.bidPaise,
        deliveryDays: dto.deliveryDays,
        coverNote: dto.coverNote,
        status: 'PENDING',
      },
    });
  }

  async findMyProposals(designer: User) {
    return this.prisma.proposal.findMany({
      where: { designerId: designer.id },
      include: {
        project: {
          select: {
            id: true,
            title: true,
            category: true,
            budgetPaise: true,
            status: true,
          },
        },
      },
      orderBy: { createdAt: 'desc' },
    });
  }

  async findForProject(projectId: string, clientId: string) {
    const project = await this.prisma.project.findUnique({
      where: { id: projectId },
    });
    if (!project) throw new NotFoundException('Project not found');
    if (project.clientId !== clientId) throw new ForbiddenException('Not your project');

    return this.prisma.proposal.findMany({
      where: { projectId },
      include: {
        designer: {
          include: {
            designerProfile: {
              select: { name: true, specializations: true, bio: true },
            },
          },
        },
      },
    });
  }
}
