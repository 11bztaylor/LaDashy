#!/bin/bash
# LaDashy Change Management Script

case "$1" in
    test-backend)
        echo "🧪 Running backend API tests..."
        cd /home/zach/homelab-documentation/ladashy_unified
        python tests/test_api_endpoints.py
        ;;
    
    test-collector)
        if [ -z "$2" ]; then
            echo "Usage: $0 test-collector <service-name>"
            exit 1
        fi
        echo "🧪 Testing $2 collector..."
        curl -X POST http://localhost:5000/api/services/$2/test-host/test \
            -H "Content-Type: application/json" \
            -d '{"host":"test-host","port":"8080"}'
        ;;
    
    add-service)
        if [ -z "$2" ]; then
            echo "Usage: $0 add-service <service-name>"
            exit 1
        fi
        echo "📝 Steps to add new service '$2':"
        echo "1. Create collector: homelab_wizard/collectors/${2}_collector.py"
        echo "2. Add to SERVICES in: homelab_wizard/services/definitions.py"
        echo "3. Register in: homelab_wizard/collectors/manager.py"
        echo "4. Test with: $0 test-collector $2"
        ;;
    
    status)
        echo "📊 LaDashy System Status"
        echo "========================"
        echo "Backend API: $(curl -s http://localhost:5000/api/health | grep -q "healthy" && echo "✅ Running" || echo "❌ Not running")"
        echo ""
        echo "Registered Collectors:"
        grep -E "\".*\": .*Collector" homelab_wizard/collectors/manager.py | sed 's/[",:]//g' | awk '{print "  ✅", $1}'
        echo ""
        echo "Saved Configurations:"
        if [ -f ~/.ladashy/service_configs.json ]; then
            echo "  $(cat ~/.ladashy/service_configs.json | grep -o '"[^"]*":' | wc -l) services configured"
        else
            echo "  No configurations saved"
        fi
        ;;
    
    backup)
        echo "💾 Creating backup..."
        timestamp=$(date +%Y%m%d_%H%M%S)
        backup_dir="backups/backup_$timestamp"
        mkdir -p $backup_dir
        cp -r ~/.ladashy $backup_dir/
        cp backend/api.py $backup_dir/
        cp -r homelab_wizard/collectors $backup_dir/
        echo "✅ Backup created: $backup_dir"
        ;;
    
    *)
        echo "LaDashy Management Tool"
        echo "======================"
        echo "Usage: $0 {test-backend|test-collector|add-service|status|backup}"
        ;;
esac
