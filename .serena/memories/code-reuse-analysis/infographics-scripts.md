# Code Reuse Analysis: Infographics Scripts

## Executive Summary

Reviewed 3 new infographics scripts for code duplication. Found **significant opportunities for refactoring** to eliminate repeated patterns:

- **CLI boilerplate**: 3 nearly-identical `main()` functions and argument parsing
- **JSON file I/O**: 5+ instances of duplicated load/save patterns
- **Directory handling**: 6+ `mkdir(parents=True, exist_ok=True)` calls scattered across files
- **Display formatting**: Repeated "section divider" and "summary table" patterns
- **Error handling**: Identical try-except-traceback pattern in all 3 files
- **Path setup**: 3 files import `sys.path.insert(0, ...)`

## Files Analyzed

1. `scripts/notebooklm_semi_auto.py` - 278 lines
2. `scripts/upload_infographics_to_supabase.py` - 223 lines
3. `scripts/upsert_game_with_infographics.py` - 191 lines

## Detailed Findings

### 1. **CLI Entry Point Boilerplate** (HIGH PRIORITY)

All 3 files duplicate:
```python
def main():
    if len(sys.argv) < N:
        print("""usage examples...""")
        sys.exit(1)
    
    args = sys.argv[1]  # or argparse.ArgumentParser
    obj = SomeClass(args)
    success = obj.run()
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()
```

**Recommendation**: Create `backend/app/utils/cli_helpers.py` with:
- `run_cli_app(app_class, args_schema)` wrapper
- Standard argument validation
- Exit code handling

---

### 2. **JSON File Operations** (HIGH PRIORITY)

Repeated 5+ times across all scripts:

```python
# Load pattern (duplicated in notebooklm_semi_auto.py, upload_infographics_to_supabase.py, upsert_game_with_infographics.py)
try:
    with open(file_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
except Exception as e:
    print(f"❌ Failed to load: {e}")
    return False

# Save pattern (duplicated in notebooklm_semi_auto.py, upload_infographics_to_supabase.py)
with open(file_path, 'w', encoding='utf-8') as f:
    json.dump(data, f, indent=2, ensure_ascii=False)
```

**Recommendation**: Create `backend/app/utils/json_io.py`:
```python
def load_json(file_path: Path) -> Optional[dict]:
    """Load JSON with error handling"""
    
def save_json(file_path: Path, data: dict, ensure_dir: bool = True) -> bool:
    """Save JSON with automatic directory creation"""
```

---

### 3. **Directory Validation & Creation** (MEDIUM PRIORITY)

Appears in all 3 files:
```python
# Pattern 1: notebooklm_semi_auto.py:57
self.output_dir.mkdir(parents=True, exist_ok=True)

# Pattern 2: upload_infographics_to_supabase.py:35
if not self.infographics_dir.exists():
    print(f"❌ Directory not found: {self.infographics_dir}")
    return False

# Pattern 3: notebooklm_semi_auto.py:193
if not self.pdf_path.exists():
    print(f"❌ PDF not found: {self.pdf_path}")
    return False
```

**Recommendation**: Create `backend/app/utils/path_helpers.py`:
```python
def ensure_directory(path: Path) -> bool:
    """Create directory with error handling"""
    
def validate_file_exists(path: Path, file_type: str = "file") -> bool:
    """Check file exists with friendly error message"""
    
def validate_directory_exists(path: Path) -> bool:
    """Check directory exists with friendly error message"""
```

---

### 4. **Display/Output Formatting** (MEDIUM PRIORITY)

Same pattern repeated in all 3 files:
```python
# Pattern appears 10+ times
print("\\n" + "=" * 75)
print("✅ SECTION TITLE HERE")
print("=" * 75)

# Indented list pattern
print(f"   • {key:20} → {value}")
```

**Recommendation**: Create `backend/app/utils/cli_display.py`:
```python
def print_section_header(title: str, width: int = 75) -> None:
    """Print formatted section header"""
    
def print_section_footer(width: int = 75) -> None:
    """Print formatted section footer"""
    
def format_key_value_list(items: dict, key_width: int = 20) -> str:
    """Format dict as aligned key-value list"""
```

---

### 5. **Error Handling Pattern** (MEDIUM PRIORITY)

Identical in all 3 files:
```python
def run(self) -> bool:
    try:
        # ... logic ...
        return True
    except KeyboardInterrupt:
        print("\\n⚠️  Cancelled by user")
        return False
    except Exception as e:
        print(f"\\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False
```

**Recommendation**: Inherit from base class:
```python
class CLIApp:
    def run(self) -> bool:
        """Wraps execute() with error handling"""
        try:
            return self.execute()
        except KeyboardInterrupt:
            print("\\n⚠️  Cancelled by user")
            return False
        except Exception as e:
            print(f"\\n❌ Error: {e}")
            import traceback
            traceback.print_exc()
            return False
    
    def execute(self) -> bool:
        """Override in subclass"""
        raise NotImplementedError
```

---

### 6. **Path Setup** (LOW PRIORITY)

Repeated in 2 files:
```python
# upload_infographics_to_supabase.py:18
# upsert_game_with_infographics.py:23
sys.path.insert(0, str(Path(__file__).parent.parent))
```

**Recommendation**: This pattern is acceptable (needed for importing from sibling directories), but document it in `.claude/rules/patterns.md`.

---

### 7. **Slug Generation** (ALREADY EXISTS)

`notebooklm_semi_auto.py:55`:
```python
self.game_slug = game_title.lower().replace(" ", "-").replace(":", "").strip()
```

**Issue**: Uses ad-hoc slugification instead of `backend/app/utils/slugify.py`

**Fix**: Import and use:
```python
from backend.app.utils.slugify import slugify
self.game_slug = slugify(game_title)
```

---

## Extraction Priority

| Priority | Item | Effort | Reuse Count | File |
|----------|------|--------|------------|------|
| HIGH | CLI entry point wrapper | 1h | 3+ scripts | `cli_helpers.py` |
| HIGH | JSON load/save | 30m | 5+ instances | `json_io.py` |
| MEDIUM | Directory validation | 30m | 6+ instances | `path_helpers.py` |
| MEDIUM | Display formatting | 30m | 10+ instances | `cli_display.py` |
| MEDIUM | Error handling base class | 45m | 3+ classes | `cli_app.py` |
| LOW | Slug generation fix | 5m | Already exists | Use `slugify.py` |

---

## Implementation Plan

### Phase 1: Extract Utilities (2 hours)
1. Create `backend/app/utils/json_io.py`
2. Create `backend/app/utils/path_helpers.py`
3. Create `backend/app/utils/cli_display.py`
4. Create `backend/app/utils/cli_app.py` (base class)
5. Create `backend/app/utils/cli_helpers.py` (argument parsing)

### Phase 2: Refactor Scripts (2 hours)
1. Update `notebooklm_semi_auto.py` to use new utilities
2. Update `upload_infographics_to_supabase.py` to use new utilities
3. Update `upsert_game_with_infographics.py` to use new utilities
4. Fix slug generation to use `slugify()`

### Phase 3: Documentation (30 min)
1. Update `backend/app/utils/README.md`
2. Document patterns in `.claude/rules/patterns.md`

---

## Code Metrics

- **Before**: 692 lines total (duplicated code ~35%)
- **After**: ~520 lines total (20% reduction)
- **Shared utilities**: ~150 lines added to `utils/`
- **Net savings**: ~180 lines

---

## Impact

✅ **Maintainability**: Future infographics scripts will have zero CLI/IO boilerplate  
✅ **Consistency**: All CLI apps follow same error handling, validation, display patterns  
✅ **Testing**: Centralized utilities are easier to unit test  
✅ **Documentation**: Single source of truth for CLI conventions  
⚠️ **Effort**: Medium (4 hours total for full refactor)
