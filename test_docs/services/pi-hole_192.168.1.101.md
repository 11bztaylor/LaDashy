# Pi-hole

## Overview

- **Host**: Unknown (192.168.1.101)
- **Port(s)**: 80, 53
- **Confidence**: 98%
- **Type**: host

## Configuration


❌ **Not Configured** - Add configuration in LaDashy to enable monitoring


## Connection Details

- **URL**: http://192.168.1.101:80



## Docker Compose Example

```yaml
version: '3.8'
services:
  pi-hole:
    image: # Add appropriate image
    container_name: pi-hole
    ports:
      - "80:80"
    volumes:
      - ./config:/config
      - ./data:/data
    environment:
      - PUID=1000
      - PGID=1000
      - TZ=America/New_York
    restart: unless-stopped
```

---
*Last Updated: 2025-07-31 14:23:17*