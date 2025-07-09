# Episode Restoration Plan

## Current Database State

### ✅ Working Series (Episodes Present)
- **Mike Hammer**: 5 episodes ✅
- **Bonanza**: 13 episodes ✅  
- **Ghost Squad**: 4 episodes (missing 2)
- **Man With a Camera**: 1 episode (missing 2)

### ❌ Missing Series (No Episodes)
- **Commando Cody**: 0 episodes (should have 12)
- **Dragnet**: 0 episodes (should have 13)
- **Longstreet**: 0 episodes (should have 30)
- **Petrocelli**: 0 episodes (should have 22)
- **Count of Monte Cristo**: 0 episodes (should have 39)

## Episode Counts by Series

| Series | Current | Target | Missing |
|--------|---------|--------|---------|
| Commando Cody | 0 | 12 | 12 |
| Dragnet | 0 | 13 | 13 |
| Man With a Camera | 1 | 3 | 2 |
| Longstreet | 0 | 30 | 30 |
| Mike Hammer | 5 | 4 | ✅ (has extra) |
| Ghost Squad | 4 | 6 | 2 |
| Petrocelli | 0 | 22 | 22 |
| Count of Monte Cristo | 0 | 39 | 39 |
| Bonanza | 13 | 13 | ✅ |

**Total Missing Episodes: 120**

## Safe Restoration Strategy

### Phase 1: Database Backup
1. Create full database backup before any changes
2. Document current episode IDs and series relationships
3. Create rollback scripts

### Phase 2: Episode Data Sources
The episode data needs to come from:
1. **Wurl metadata files** (CSV/Excel files in root directory)
2. **Existing episode restoration scripts** in `/scripts/` folder
3. **Episode files** in `/pecantv_series/` folders

### Phase 3: Restoration Priority
**High Priority (Most Important):**
1. **Petrocelli** (22 episodes) - User specifically mentioned this
2. **Dragnet** (13 episodes) - Classic series
3. **Commando Cody** (12 episodes) - User specifically mentioned this

**Medium Priority:**
4. **Longstreet** (30 episodes)
5. **Count of Monte Cristo** (39 episodes)

**Low Priority:**
6. **Ghost Squad** (2 missing episodes)
7. **Man With a Camera** (2 missing episodes)

## Episode Data Sources

### Available Scripts with Episode Data
- `/scripts/fix_petrocelli_episodes.py` - Contains Petrocelli episode data
- `/scripts/fix_dragnet_episodes.py` - Contains Dragnet episode data  
- `/scripts/fix_commando_cody_episodes.py` - Contains Commando Cody episode data
- `/scripts/fix_longstreet_episodes.py` - Contains Longstreet episode data
- `/scripts/fix_count_of_monte_cristo_episodes.py` - Contains CMC episode data

### Wurl Metadata Files
- `Wurl - File Upload Metadata_Version 7.0.64.csv` - Latest metadata
- Multiple Excel versions available for cross-reference

### Episode Files
- `/pecantv_series/petrocelli/` - Contains episode files
- `/pecantv_series/dragnet/` - Contains episode files
- `/pecantv_series/commando_cody/` - Contains episode files
- `/pecantv_series/longstreet/` - Contains episode files
- `/pecantv_series/count_of_monte_cristo/` - Contains episode files

## Restoration Scripts Needed

### 1. Database Backup Script
```python
# backup_current_episodes.py
# Creates backup of current episodes table
```

### 2. Petrocelli Restoration (22 episodes)
```python
# restore_petrocelli_episodes.py
# Uses data from fix_petrocelli_episodes.py
# Target: 22 episodes
```

### 3. Dragnet Restoration (13 episodes)  
```python
# restore_dragnet_episodes.py
# Uses data from fix_dragnet_episodes.py
# Target: 13 episodes
```

### 4. Commando Cody Restoration (12 episodes)
```python
# restore_commando_cody_episodes.py
# Uses data from fix_commando_cody_episodes.py
# Target: 12 episodes
```

### 5. Longstreet Restoration (30 episodes)
```python
# restore_longstreet_episodes.py
# Uses data from fix_longstreet_episodes.py
# Target: 30 episodes
```

### 6. Count of Monte Cristo Restoration (39 episodes)
```python
# restore_count_of_monte_cristo_episodes.py
# Uses data from fix_count_of_monte_cristo_episodes.py
# Target: 39 episodes
```

### 7. Ghost Squad Completion (2 episodes)
```python
# complete_ghost_squad_episodes.py
# Add missing 2 episodes to existing 4
```

### 8. Man With a Camera Completion (2 episodes)
```python
# complete_man_with_camera_episodes.py
# Add missing 2 episodes to existing 1
```

## Safety Measures

### Before Restoration
1. **Full database backup**
2. **Document current episode IDs**
3. **Create rollback scripts**
4. **Test on small subset first**

### During Restoration
1. **One series at a time**
2. **Verify each episode insertion**
3. **Check for duplicates**
4. **Validate episode numbers**

### After Restoration
1. **Verify episode counts**
2. **Test API endpoints**
3. **Check episode playback**
4. **Validate poster images**

## Expected Results

After restoration:
- **Total episodes**: 143 (23 current + 120 missing)
- **All series will have their episodes**
- **API will serve complete episode lists**
- **App will show all episodes in carousels**

## Rollback Plan

If issues occur:
1. **Restore from database backup**
2. **Remove newly added episodes**
3. **Revert to current working state**

## Next Steps

1. **Review this plan**
2. **Approve restoration approach**
3. **Create backup scripts**
4. **Start with high-priority series**
5. **Test each restoration**
6. **Verify app functionality**

## Questions for Review

1. **Priority order**: Which series should be restored first?
2. **Testing approach**: How should we test each restoration?
3. **Rollback strategy**: What's the acceptable rollback time?
4. **Verification**: How should we verify episodes are working in the app? 