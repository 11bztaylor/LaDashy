# Plex

## Overview

- **Host**: Unknown (192.168.1.100)
- **Port(s)**: 32400
- **Confidence**: 95%
- **Type**: docker

## Configuration


### Current Configuration
```yaml
{
  "host": "192.168.1.100",
  "port": 32400,
  "token": "test-token-123"
}
```


## Connection Details

- **URL**: http://192.168.1.100:32400



## Docker Compose Example

```yaml
version: '3.8'
services:
  plex:
    image: # Add appropriate image
    container_name: plex
    ports:
      - "32400:32400"
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