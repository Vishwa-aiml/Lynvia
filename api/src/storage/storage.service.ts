import { Injectable, Logger } from '@nestjs/common';
import { ConfigService } from '@nestjs/config';
import {
  S3Client,
  PutObjectCommand,
  DeleteObjectCommand,
} from '@aws-sdk/client-s3';
import { getSignedUrl } from '@aws-sdk/s3-request-presigner';
import { GetObjectCommand } from '@aws-sdk/client-s3';

export type S3UrlType = 'preview' | 'delivery';

@Injectable()
export class StorageService {
  private readonly client: S3Client;
  private readonly bucket: string;
  private readonly previewTtl: number;
  private readonly deliveryTtl: number;
  private readonly logger = new Logger(StorageService.name);

  constructor(private config: ConfigService) {
    this.client = new S3Client({
      region: config.getOrThrow<string>('AWS_REGION'),
      credentials: {
        accessKeyId: config.getOrThrow<string>('AWS_ACCESS_KEY_ID'),
        secretAccessKey: config.getOrThrow<string>('AWS_SECRET_ACCESS_KEY'),
      },
    });

    this.bucket = config.getOrThrow<string>('AWS_S3_BUCKET_NAME');
    this.previewTtl = parseInt(config.get('S3_PREVIEW_URL_TTL') ?? '900', 10);
    this.deliveryTtl = parseInt(config.get('S3_DELIVERY_URL_TTL') ?? '300', 10);
  }

  /**
   * Generates a pre-signed GET URL for a private S3 object.
   * TTL depends on whether it's a preview or a final delivery file.
   *
   * RULE: Never issue a permanent/public URL. Always call this server-side
   * AFTER verifying the requester is a participant on the resource.
   */
  async getSignedUrl(key: string, type: S3UrlType): Promise<string> {
    const ttl = type === 'delivery' ? this.deliveryTtl : this.previewTtl;

    const command = new GetObjectCommand({
      Bucket: this.bucket,
      Key: key,
    });

    return getSignedUrl(this.client, command, { expiresIn: ttl });
  }

  /**
   * Generates a pre-signed PUT URL for direct browser-to-S3 upload.
   * The client uploads directly to S3; the server never proxies file bytes.
   * TTL is 10 minutes — enough for any reasonable upload.
   */
  async getUploadUrl(
    key: string,
    contentType: string,
  ): Promise<{ uploadUrl: string; key: string }> {
    const command = new PutObjectCommand({
      Bucket: this.bucket,
      Key: key,
      ContentType: contentType,
    });

    const uploadUrl = await getSignedUrl(this.client, command, {
      expiresIn: 600, // 10 minutes
    });

    return { uploadUrl, key };
  }

  /**
   * Deletes an S3 object. Called when a project is cancelled or a file
   * is replaced. Only call after verifying requester owns the resource.
   */
  async deleteObject(key: string): Promise<void> {
    const command = new DeleteObjectCommand({
      Bucket: this.bucket,
      Key: key,
    });

    await this.client.send(command);
    this.logger.log(`Deleted S3 object: ${key}`);
  }

  /**
   * Generates a structured S3 key for a portfolio image.
   * Format: portfolios/{userId}/{timestamp}-{filename}
   */
  portfolioKey(userId: string, filename: string): string {
    const ts = Date.now();
    const sanitized = filename.replace(/[^a-zA-Z0-9.\-_]/g, '_');
    return `portfolios/${userId}/${ts}-${sanitized}`;
  }

  /**
   * Generates a structured S3 key for a project delivery file.
   * Format: projects/{projectId}/delivery/{timestamp}-{filename}
   */
  deliveryKey(projectId: string, filename: string): string {
    const ts = Date.now();
    const sanitized = filename.replace(/[^a-zA-Z0-9.\-_]/g, '_');
    return `projects/${projectId}/delivery/${ts}-${sanitized}`;
  }
}
