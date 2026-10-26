import { Injectable, NotFoundException, ForbiddenException, ConflictException } from '@nestjs/common';
import { PrismaService } from '../prisma/prisma.service';
import { ProjectStatus, User } from '@prisma/client';
import { CreateProjectDto } from './dto/create-project.dto';

/**
 * ProjectsService
 *
 * ALL project state transitions go through this service.
 * Status is NEVER set directly in a controller.
 */
@Injectable()
export class ProjectsService {
  constructor(private prisma: PrismaService) {}

  async create(client: User, dto: CreateProjectDto) {
    return this.prisma.project.create({
      data: {
        clientId: client.id,
        title: dto.title,
        brief: dto.brief,
        category: dto.category,
        budgetPaise: dto.budgetPaise,
        status: ProjectStatus.OPEN,
      },
    });
  }

  async findAllOpen() {
    return this.prisma.project.findMany({
      where: { status: ProjectStatus.OPEN },
      include: {
        client: {
          select: { id: true, email: true },
        },
        _count: { select: { proposals: true } },
      },
      orderBy: { createdAt: 'desc' },
    });
  }

  async findMyProjects(client: User) {
    return this.prisma.project.findMany({
      where: { clientId: client.id },
      include: {
        _count: { select: { proposals: true } },
      },
      orderBy: { createdAt: 'desc' },
    });
  }

  async findOne(id: string, requesterId: string, requesterRole: string) {
    const project = await this.prisma.project.findUnique({
      where: { id },
      include: {
        client: { select: { id: true, email: true } },
        proposals: {
          include: {
            designer: {
              include: {
                designerProfile: {
                  select: {
                    name: true,
                    specializations: true,
                    vettingStatus: true,
                  },
                },
              },
            },
          },
        },
      },
    });

    if (!project) throw new NotFoundException('Project not found');

    // Non-admin, non-client-owner can only see OPEN projects
    const isOwner = project.clientId === requesterId;
    const isAdmin = requesterRole === 'ADMIN';

    if (!isOwner && !isAdmin && project.status !== ProjectStatus.OPEN) {
      throw new ForbiddenException('Access denied');
    }

    // Security & privacy: only project owner and admin see all competing proposals.
    // Designers only see their own proposal if they submitted one.
    if (!isOwner && !isAdmin) {
      return {
        ...project,
        proposals: project.proposals.filter((p) => p.designerId === requesterId),
      };
    }

    return project;
  }

  /** State transition: OPEN → PROPOSAL_ACCEPTED */
  async acceptProposal(projectId: string, proposalId: string, clientId: string) {
    const project = await this.prisma.project.findUnique({
      where: { id: projectId },
    });

    if (!project) throw new NotFoundException('Project not found');
    if (project.clientId !== clientId) throw new ForbiddenException('Not your project');
    if (project.status !== ProjectStatus.OPEN) {
      throw new ConflictException(`Cannot accept proposal — project is ${project.status}`);
    }

    // Atomic transaction: accept one proposal, reject all others, update project status
    return this.prisma.$transaction(async (tx) => {
      await tx.proposal.updateMany({
        where: { projectId, id: { not: proposalId }, status: 'PENDING' },
        data: { status: 'REJECTED' },
      });

      await tx.proposal.update({
        where: { id: proposalId },
        data: { status: 'ACCEPTED' },
      });

      return tx.project.update({
        where: { id: projectId },
        data: { status: ProjectStatus.PROPOSAL_ACCEPTED },
      });
    });
  }

  /** Validates ownership — used by other services */
  async assertOwnership(projectId: string, clientId: string) {
    const project = await this.prisma.project.findUnique({
      where: { id: projectId },
    });
    if (!project) throw new NotFoundException('Project not found');
    if (project.clientId !== clientId) throw new ForbiddenException('Not your project');
    return project;
  }
}
