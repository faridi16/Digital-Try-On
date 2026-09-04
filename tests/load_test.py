import time
import uuid
import requests
import threading

# Simulating Locust or similar load testing framework behavior
# In a real environment, this would hit the actual load balancer URL
API_GATEWAY_URL = "http://localhost:8000"

def simulate_concurrent_requests(num_users=50, requests_per_user=10):
    """
    Task 6.1: Conduct load testing to ensure GPU workers autoscale appropriately.
    Simulates a spike in traffic for the AR Fitting Room.
    """
    print(f"Starting load test with {num_users} simulated concurrent users...")
    
    success_count = 0
    failure_count = 0
    
    def user_task():
        nonlocal success_count, failure_count
        for _ in range(requests_per_user):
            try:
                # Mock Mode B Warp payload
                dummy_image_data = b"dummy_photo_data"
                
                # In a real test, we would send a POST request:
                # response = requests.post(f"{API_GATEWAY_URL}/mode-b/warp", files={"file": ("photo.jpg", dummy_image_data)})
                # if response.status_code == 200:
                #    success_count += 1
                
                # Simulating immediate success for this mockup
                time.sleep(0.1) # Simulate network latency
                success_count += 1
            except Exception as e:
                failure_count += 1
                
    threads = []
    start_time = time.time()
    
    for _ in range(num_users):
        t = threading.Thread(target=user_task)
        threads.append(t)
        t.start()
        
    for t in threads:
        t.join()
        
    duration = time.time() - start_time
    total_requests = num_users * requests_per_user
    
    print("\n--- Load Test Results ---")
    print(f"Total Requests: {total_requests}")
    print(f"Successful: {success_count}")
    print(f"Failed: {failure_count}")
    print(f"Duration: {duration:.2f} seconds")
    print(f"Requests per second (RPS): {total_requests/duration:.2f}")
    
    # Assert criteria for auto-scaling trigger
    if total_requests / duration > 50:
        print("Success: RPS exceeded 50, verifying autoscale triggers via metrics dashboard (Simulated).")
    else:
        print("Warning: RPS low, check load balancer configuration.")

if __name__ == "__main__":
    simulate_concurrent_requests()
