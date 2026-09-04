import React from 'react';
import { render, waitFor } from '@testing-library/react-native';
import FittingRoomRenderer from '../components/FittingRoomRenderer';
import MemoryManager from '../utils/MemoryManager';

// Mock the memory manager
jest.mock('../utils/MemoryManager', () => ({
  addTexture: jest.fn()
}));

// Mock console to avoid noisy test output
global.console = {
  log: jest.fn(),
  warn: jest.fn(),
  error: jest.fn()
};

describe('FittingRoomRenderer (Task 6.2 - Thermal Throttling / Timeout)', () => {
  
  beforeEach(() => {
    jest.useFakeTimers();
    jest.clearAllMocks();
  });

  afterEach(() => {
    jest.useRealTimers();
  });

  test('should trigger fallback if rendering takes longer than 3 seconds', async () => {
    const mockOnTimeoutFallback = jest.fn();
    const mockItem = { id: '1', name: 'Test Shirt' };
    
    // We mock a scenario where the load takes longer than 3 seconds
    // In our component, simulateLoad uses setTimeout for 1.5s, 
    // but we want to simulate the fallback being called before it finishes, 
    // or simulate a longer delay.
    
    render(
      <FittingRoomRenderer 
        item={mockItem} 
        mode="B" 
        onTimeoutFallback={mockOnTimeoutFallback} 
      />
    );
    
    // Fast-forward time by 3000ms (the TIMEOUT_CEILING_MS)
    jest.advanceTimersByTime(3000);
    
    // The fallback should have been triggered
    await waitFor(() => {
      expect(mockOnTimeoutFallback).toHaveBeenCalled();
      expect(console.warn).toHaveBeenCalledWith(
        expect.stringContaining('Fitting Room Render Timeout: 3-second ceiling reached')
      );
    });
  });

  test('should successfully load if under 3 seconds and within memory limits', async () => {
    const mockOnTimeoutFallback = jest.fn();
    const mockItem = { id: '2', name: 'Test Pants' };
    
    // Mock the memory manager to succeed
    MemoryManager.addTexture.mockReturnValue(true);

    const { getByText } = render(
      <FittingRoomRenderer 
        item={mockItem} 
        mode="A" 
        onTimeoutFallback={mockOnTimeoutFallback} 
      />
    );
    
    // Fast forward just the 1500ms simulateLoad time
    jest.advanceTimersByTime(1500);
    
    // Wait for the async state update
    await waitFor(() => {
      expect(getByText('[3D Viewport rendered for Test Pants]')).toBeTruthy();
      expect(mockOnTimeoutFallback).not.toHaveBeenCalled();
    });
  });
});
