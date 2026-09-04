import MemoryManager from '../utils/MemoryManager';

// Mocking the console to keep test output clean, but allowing us to spy on it
global.console = {
  log: jest.fn(),
  warn: jest.fn(),
  error: jest.fn()
};

describe('MemoryManager (Task 6.2 - OOM Prevention)', () => {
  
  beforeEach(() => {
    MemoryManager.clearCache();
    jest.clearAllMocks();
  });

  test('should cache textures within the 150MB threshold', () => {
    const success1 = MemoryManager.addTexture('tex1', 'data1', 50);
    const success2 = MemoryManager.addTexture('tex2', 'data2', 50);
    
    expect(success1).toBe(true);
    expect(success2).toBe(true);
    expect(MemoryManager.currentMemoryUsageMB).toBe(100);
  });

  test('should trigger aggressive garbage collection when approaching threshold', () => {
    // Fill up to 120MB
    MemoryManager.addTexture('tex1', 'data1', 40);
    MemoryManager.addTexture('tex2', 'data2', 40);
    MemoryManager.addTexture('tex3', 'data3', 40);
    
    // Add 40MB more, which breaches the 150MB threshold (160MB total)
    const success4 = MemoryManager.addTexture('tex4', 'data4', 40);
    
    // It should have successfully added by evicting older textures
    expect(success4).toBe(true);
    
    // Check that a warning was logged indicating threshold breach & GC run
    expect(console.warn).toHaveBeenCalledWith(
      expect.stringContaining('Memory limit reached (150MB). Running GC')
    );
    
    // Assuming GC removes half the cache (2 items in this case), usage should be lower
    expect(MemoryManager.currentMemoryUsageMB).toBeLessThan(150);
    
    // tex1 should be evicted (as it was the oldest)
    expect(MemoryManager.getTexture('tex1')).toBeNull();
  });

  test('should refuse to cache if a single texture exceeds the threshold even after GC', () => {
    const success = MemoryManager.addTexture('texHuge', 'data', 200);
    
    expect(success).toBe(false);
    expect(console.error).toHaveBeenCalledWith(
      expect.stringContaining('Out of memory constraints')
    );
    expect(MemoryManager.currentMemoryUsageMB).toBe(0);
  });
});
