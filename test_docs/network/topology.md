# Network Topology

## Network Diagram

```mermaid
graph TB
    subgraph Internet
        WAN[Internet]
    end
    
    subgraph "Home Network"
        Router[Router<br/>192.168.1.1]
        WAN --> Router

        192_168_1_100[unraid-server<br/>192.168.1.100<br/>Plex<br/>Radarr]
        Router --> 192_168_1_100
        192_168_1_101[raspberry-pi<br/>192.168.1.101<br/>Pi-hole]
        Router --> 192_168_1_101
    end
```

## Host Details

| Hostname | IP Address | Services | Open Ports |
|----------|------------|----------|------------|
| unraid-server | 192.168.1.100 | Plex, Radarr | 32400, 7878 |
| raspberry-pi | 192.168.1.101 | Pi-hole | 80, 53 |


---
*Generated: 2025-07-31 14:23:17*