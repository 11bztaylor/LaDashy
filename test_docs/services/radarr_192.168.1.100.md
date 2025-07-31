# Radarr

## Overview

- **Host**: Unknown (192.168.1.100)
- **Port(s)**: 7878
- **Confidence**: 90%
- **Type**: docker

## Configuration


### Current Configuration
```yaml
{
  "api_key": "test-api-key",
  "host": "192.168.1.100",
  "port": 7878
}
```


## Connection Details

- **URL**: http://192.168.1.100:7878

- **API Key**: ✅ Configured



## Docker Compose Example

```yaml
version: '3.8'
services:
  radarr:
    image: # Add appropriate image
    container_name: radarr
    ports:
      - "7878:7878"
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