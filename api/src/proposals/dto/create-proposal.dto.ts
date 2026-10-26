import { IsString, IsInt, IsPositive, IsOptional, MaxLength, Min, Max } from 'class-validator';
import { Transform } from 'class-transformer';

export class CreateProposalDto {
  @IsString()
  projectId: string;

  /**
   * Bid in integer paise. Min ₹100 = 10000 paise. Max ₹20,00,000 = 200,000,000 paise.
   */
  @IsInt()
  @Min(10000, { message: 'Minimum bid is ₹100 (10000 paise)' })
  @Max(200000000, { message: 'Maximum bid is ₹20,00,000 (200000000 paise)' })
  bidPaise: number;

  @IsInt()
  @IsPositive()
  @Max(365, { message: 'Delivery days cannot exceed 365 days' })
  deliveryDays: number;

  @IsOptional()
  @Transform(({ value }) => (typeof value === 'string' ? value.trim() : value))
  @IsString()
  @MaxLength(1000)
  coverNote?: string;
}

