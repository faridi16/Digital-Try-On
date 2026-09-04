// mock React Native module
import { AppState } from 'react-native';

class MemoryManager {
  constructor() {
    this.textureCache = new Map();
    this.memoryThresholdMB = 150; // Strict limit for mid-range Android devices
    this.currentMemoryUsageMB = 0;
    
    // Listen to app state changes (e.g., going to background) to trigger GC
    AppState.addEventListener('change', this.handleAppStateChange.bind(this));
  }

  handleAppStateChange(nextAppState) {
    if (nextAppState === 'background') {
      console.log('App in background, triggering aggressive garbage collection.');
      this.clearCache();
    }
  }

  /**
   * Adds a texture to the cache if within limits. 
   * Triggers cleanup if memory limit is approached.
   */
  addTexture(textureId, textureData, sizeInMB) {
    if (this.currentMemoryUsageMB + sizeInMB > this.memoryThresholdMB) {
      console.warn(`Memory limit reached (${this.memoryThresholdMB}MB). Running GC before caching ${textureId}.`);
      this.runGarbageCollection();
    }
    
    // If still over limit after GC, do not cache
    if (this.currentMemoryUsageMB + sizeInMB > this.memoryThresholdMB) {
      console.error(`Cannot cache ${textureId} (Size: ${sizeInMB}MB). Out of memory constraints.`);
      return false;
    }
    
    this.textureCache.set(textureId, { data: textureData, size: sizeInMB, lastAccessed: Date.now() });
    this.currentMemoryUsageMB += sizeInMB;
    console.log(`Cached texture ${textureId}. Current usage: ${this.currentMemoryUsageMB}MB`);
    return true;
  }

  getTexture(textureId) {
    if (this.textureCache.has(textureId)) {
      const texture = this.textureCache.get(textureId);
      texture.lastAccessed = Date.now();
      return texture.data;
    }
    return null;
  }

  /**
   * Aggressive garbage collection: remove least recently used textures.
   */
  runGarbageCollection() {
    console.log('Running aggressive garbage collection on texture cache...');
    
    // Sort textures by last accessed time
    const sortedTextures = Array.from(this.textureCache.entries())
      .sort((a, b) => a[1].lastAccessed - b[1].lastAccessed);
      
    // Remove the oldest half of the cache
    const itemsToRemove = Math.ceil(sortedTextures.length / 2);
    
    for (let i = 0; i < itemsToRemove; i++) {
      const [id, texture] = sortedTextures[i];
      this.textureCache.delete(id);
      this.currentMemoryUsageMB -= texture.size;
      console.log(`Evicted texture ${id}. Freed ${texture.size}MB.`);
    }
    
    console.log(`GC completed. Current usage: ${this.currentMemoryUsageMB}MB`);
  }
  
  clearCache() {
    this.textureCache.clear();
    this.currentMemoryUsageMB = 0;
    console.log('Texture cache cleared.');
  }
}

export default new MemoryManager();
