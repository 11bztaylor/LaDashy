# LaDashy Regression Test Checklist

## After Any Backend Change

### 1. Core API Tests
- [ ] Health endpoint returns 200
- [ ] Service definitions load
- [ ] Network discovery runs without error

### 2. Service Tests (for each service type)
- [ ] Test connection works
- [ ] Save configuration works
- [ ] Load configuration works
- [ ] Collector returns data

### 3. Integration Tests
- [ ] Frontend can call all endpoints
- [ ] Saved configs persist across restarts
- [ ] Dashboard generation creates valid output

## Quick Test Commands

Test all endpoints:
    ./tests/test_api_endpoints.py

Test specific service:
    curl -X POST http://localhost:5000/api/services/radarr/192.168.100.4/test \
      -H "Content-Type: application/json" \
      -d '{"host":"192.168.100.4","port":"7878","api_key":"2f6a1fd0aeda49dca9226e740162fb49"}'

Check system status:
    ./manage_changes.sh status

## Adding New Services

1. Create collector file
2. Update definitions
3. Register in manager
4. Run: ./manage_changes.sh test-collector <service-name>
5. Update this checklist
