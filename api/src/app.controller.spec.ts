import { Test, TestingModule } from '@nestjs/testing';
import { AppController } from './app.controller.js';
import { AppService } from './app.service.js';
import { describe, beforeEach, it, expect } from 'vitest';

describe('AppController', () => {
  let appController: AppController;

  beforeEach(async () => {
    const app: TestingModule = await Test.createTestingModule({
      controllers: [AppController],
      providers: [AppService],
    }).compile();

    appController = app.get<AppController>(AppController);
  });

  describe('health check', () => {
    it('should return service health status with ok and timestamp', () => {
      const result = appController.getHealth();
      expect(result.status).toBe('ok');
      expect(result.service).toBe('lynvia-api');
      expect(result.timestamp).toBeDefined();
    });
  });
});
