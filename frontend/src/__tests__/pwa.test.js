/**
 * Tests for PWA and offline support utilities
 */

import {
  registerServiceWorker,
  getOnlineStatus,
  cachePostsForOffline,
} from '../utils/pwa';

// Mock db module
jest.mock('../utils/db', () => ({
  initDB: jest.fn().mockResolvedValue({}),
  savePosts: jest.fn().mockResolvedValue(undefined),
  getPendingPosts: jest.fn().mockResolvedValue([]),
  removePendingPost: jest.fn().mockResolvedValue(undefined),
}));

describe('PWA Utils', () => {
  beforeEach(() => {
    jest.clearAllMocks();
    global.console.log = jest.fn();
    global.console.warn = jest.fn();
    global.console.error = jest.fn();
  });

  describe('registerServiceWorker', () => {
    it('should register service worker successfully', async () => {
      const mockRegistration = {
        scope: '/',
      };

      global.navigator.serviceWorker = {
        register: jest.fn().mockResolvedValue(mockRegistration),
        addEventListener: jest.fn(),
        controller: null,
      };

      const result = await registerServiceWorker();

      expect(result).toEqual(mockRegistration);
      expect(global.navigator.serviceWorker.register).toHaveBeenCalledWith(
        '/service-worker.js',
        { scope: '/' }
      );
    });

    it('should handle service workers not supported', async () => {
      delete global.navigator.serviceWorker;

      const result = await registerServiceWorker();

      expect(result).toBeNull();
      expect(global.console.warn).toHaveBeenCalledWith('Service Workers not supported');
    });

    it('should handle registration error', async () => {
      const error = new Error('Registration failed');

      global.navigator.serviceWorker = {
        register: jest.fn().mockRejectedValue(error),
        addEventListener: jest.fn(),
        controller: null,
      };

      const result = await registerServiceWorker();

      expect(result).toBeNull();
      expect(global.console.error).toHaveBeenCalledWith('Failed to register Service Worker:', error);
    });

    it('should add message listener when service worker is active', async () => {
      const mockRegistration = { scope: '/' };

      global.navigator.serviceWorker = {
        register: jest.fn().mockResolvedValue(mockRegistration),
        addEventListener: jest.fn(),
        controller: {
          postMessage: jest.fn(),
        },
      };

      await registerServiceWorker();

      expect(global.navigator.serviceWorker.addEventListener).toHaveBeenCalledWith(
        'message',
        expect.any(Function)
      );
      expect(global.navigator.serviceWorker.controller.postMessage).toHaveBeenCalledWith({
        type: 'SYNC_CHECK',
      });
    });
  });

  describe('getOnlineStatus', () => {
    it('should return current online status', () => {
      global.navigator.onLine = true;
      const status = getOnlineStatus();
      expect(typeof status).toBe('boolean');
    });
  });

  describe('cachePostsForOffline', () => {
    it('should cache posts for offline use', async () => {
      const dbModule = require('../utils/db');
      const mockPosts = [
        { id: '1', content: 'Post 1' },
        { id: '2', content: 'Post 2' },
      ];

      await cachePostsForOffline(mockPosts);

      expect(dbModule.savePosts).toHaveBeenCalledWith(mockPosts);
      expect(global.console.log).toHaveBeenCalledWith('Cached 2 posts for offline use');
    });

    it('should handle caching errors gracefully', async () => {
      const dbModule = require('../utils/db');
      const error = new Error('Cache failed');
      dbModule.savePosts.mockRejectedValueOnce(error);

      await cachePostsForOffline([{ id: '1', content: 'Post 1' }]);

      expect(global.console.error).toHaveBeenCalledWith('Failed to cache posts:', error);
    });
  });

  describe('Offline support initialization', () => {
    it('should initialize PWA utils without errors', async () => {
      global.navigator.serviceWorker = {
        register: jest.fn().mockResolvedValue({ scope: '/' }),
        addEventListener: jest.fn(),
        controller: null,
      };

      global.window = {
        addEventListener: jest.fn(),
        dispatchEvent: jest.fn(),
      };

      // Just verify no errors are thrown
      await expect(cachePostsForOffline([])).resolves.toBeUndefined();
    });
  });

  describe('Service Worker message handling', () => {
    it('should register service worker with message handler', async () => {
      const mockRegistration = { scope: '/' };

      global.navigator.serviceWorker = {
        register: jest.fn().mockResolvedValue(mockRegistration),
        addEventListener: jest.fn(),
        controller: null,
      };

      await registerServiceWorker();

      // Verify message listener was added
      expect(global.navigator.serviceWorker.addEventListener).toHaveBeenCalledWith(
        'message',
        expect.any(Function)
      );
    });
  });
});
