# LaDashy Project Manager - AI Session Guide

## 🤖 AI Instructions - READ THIS FIRST

This document is the master index for the LaDashy project. When starting a new conversation:
1. Start by reading this document
2. Look up the section you're working on
3. Check the current status
4. Review session history for that section

## 🗂️ Master Section Index

### SECTION_01_BACKEND_API
**Purpose**: Flask API backend and service endpoints
**Current Status**: ✅ Test endpoint working
**Problem**: manager.get_collector() not receiving config parameter
**Key Files**: 
- backend/api.py (test_service route)
- homelab_wizard/collectors/manager.py
**Quick Test**: Use curl to test the endpoint with JSON payload

### SECTION_02_FRONTEND_STATE
**Purpose**: Service state management and UI updates
**Current Status**: ⚠️ Services appear in wrong sections
**Problem**: Manual services not marked as configured, missing API key field
**Key Functions**:
- addManualService() - Has duplicate const declaration
- updateServiceGrid() - Section logic issue

### SECTION_03_ICON_SYSTEM
**Purpose**: Service icon loading and fallbacks
**Current Status**: ⚠️ Many 404 errors
**Problem**: No emoji fallback system implemented

### SECTION_04_DASHBOARD_GEN
**Purpose**: Generate Dashy YAML configuration
**Current Status**: ❌ Not implemented
**Problem**: generateDashboard() function empty

### SECTION_05_COLLECTORS
**Purpose**: Service-specific data collectors
**Current Status**: ✅ Basic working
**Working**: Plex, Radarr, Sonarr
**Need**: Home Assistant, Docker stats

## 🔄 Status Symbols
- ✅ Working
- ⚠️ Partially working/Has issues  
- ❌ Broken/Not implemented
- 🚧 In progress

## 🚀 Quick Commands
Navigate and activate:
cd /home/zach/homelab-documentation/ladashy_unified
source ../homelab-env/bin/activate

Run server:
python backend/api.py

Quick save documentation:
git add docs/project_knowledge && git commit -m "[DOCS] Update" && git push
