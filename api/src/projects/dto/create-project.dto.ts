import {
  IsString,
  IsInt,
  MaxLength,
  IsEnum,
  Min,
  Max,
} from 'class-validator';
import { Transform } from 'class-transformer';

export class CreateProjectDto {
  @Transform(({ value }) => (typeof value === 'string' ? value.trim() : value))
  @IsString()
  @MaxLength(150)
  title: string;

  @Transform(({ value }) => (typeof value === 'string' ? value.trim() : value))
  @IsString()
  @MaxLength(5000)
  brief: string;

  @IsEnum(['logo_branding', 'poster_social'], {
    message: 'category must be logo_branding or poster_social',
  })
  category: 'logo_branding' | 'poster_social';

  /**
   * Budget in integer paise. Frontend converts ₹ → paise before sending.
   * Min ₹500 = 50000 paise. Max ₹20,00,000 = 200,000,000 paise (protects against 32-bit DB overflow).
   */
  @IsInt()
  @Min(50000, { message: 'Minimum budget is ₹500 (50000 paise)' })
  @Max(200000000, { message: 'Maximum budget is ₹20,00,000 (200000000 paise)' })
  budgetPaise: number;
}

