# DeclarativeX Upgrade Plan

## Executive Summary

This document outlines a comprehensive upgrade plan for the DeclarativeX project, including dependency updates, security improvements, code modernization, and Python version support enhancements.

**Date:** 2026-02-15  
**Current Version:** 1.0.0  
**Status:** ✅ All linters passing, 100% code coverage maintained

---

## 🐛 Bug Fixes Implemented

### 1. Proxy Configuration Override Bug
**Issue:** Method-level proxies were not properly overriding class-level proxies due to incorrect merge order in `executors.py`.

**Root Cause:** The merge operation was called as `method_config.merge(class_config)` when it should have been `class_config.merge(method_config)` to ensure method-level settings take precedence.

**Fix Applied:**
- Fixed merge order in `src/declarativex/executors.py` line 94-97
- All proxy tests now passing (7/7)

### 2. httpx Auth Support Missing
**Issue:** The library only supported custom `Auth` classes but not native `httpx.Auth` types like `httpx.BasicAuth`.

**Root Cause:** Auth was not being passed to `httpx.Client`/`httpx.AsyncClient` constructors, and type hints didn't allow httpx auth types.

**Fixes Applied:**
- Added `Union[Auth, httpx.Auth]` type hints in `client.py` and `models.py`
- Updated `RawRequest.initialize()` to conditionally apply auth based on type
- Added `_get_httpx_auth()` helper method to executors
- Pass auth to `httpx.Client` and `httpx.AsyncClient` constructors
- Maintains backward compatibility with existing `Auth` classes

---

## 📦 Dependency Upgrade Recommendations

### Critical Updates (High Priority)

#### 1. **httpx: 0.25.2 → 0.28.1**
- **Priority:** HIGH
- **Breaking Changes:** Minor API improvements
- **Benefits:**
  - Security patches
  - Performance improvements
  - Better HTTP/2 support
- **Action:** Update to `^0.28.0` or `^0.27.0` for stability
- **Risk:** Low - httpx maintains good backward compatibility

#### 2. **pydantic: 2.5.3 → 2.12.5**
- **Priority:** HIGH
- **Breaking Changes:** None within v2.x
- **Benefits:**
  - Performance improvements (up to 50% faster validation)
  - Bug fixes
  - Better type checking
- **Action:** Update to `^2.12.0`
- **Risk:** Very Low - v2.x is stable

#### 3. **h2: 4.1.0 → 4.3.0**
- **Priority:** MEDIUM
- **Breaking Changes:** None
- **Benefits:**
  - Bug fixes
  - Improved HTTP/2 compliance
- **Action:** Update to `>=3,<5` (already allows 4.3.0)
- **Risk:** Very Low

### Development Dependencies Updates

#### Testing Framework
- **pytest: 7.4.4 → 9.0.2** (MAJOR update)
  - Priority: MEDIUM
  - Requires testing for compatibility
  - Consider incremental update: 7.4.4 → 8.x → 9.x
  
- **pytest-asyncio: 0.21.1 → 1.3.0** (MAJOR update)
  - Priority: MEDIUM
  - May require test changes
  
- **pytest-xdist: 3.5.0 → 3.8.0**
  - Priority: LOW
  - Safe minor update

#### Code Quality Tools
- **mypy: 1.8.0 → 1.19.1**
  - Priority: MEDIUM
  - Better type checking
  - May catch new type issues
  
- **pylint: 3.0.3 → 4.0.4** (MAJOR update)
  - Priority: LOW
  - May introduce new checks
  - Test before upgrading
  
- **flake8: 6.1.0 → 7.3.0** (MAJOR update)
  - Priority: LOW
  - New style checks
  - Review before upgrading

#### Documentation
- **mkdocs-material: 9.5.4 → 9.7.1**
  - Priority: LOW
  - UI improvements
  - Safe to update

---

## 🔒 Security Analysis

### Current Status: ✅ SECURE
- **No known vulnerabilities** in production dependencies
- All dependencies scanned against GitHub Advisory Database
- Core dependencies (httpx, pydantic) are secure

### Recommendations:
1. Set up automated dependency scanning (Dependabot, Renovate)
2. Update dependencies quarterly
3. Monitor CVEs for httpx and pydantic specifically
4. Consider adding `safety` or `pip-audit` to CI pipeline

---

## 🐍 Python Version Support

### Current Support
- **Minimum:** Python 3.9
- **Maximum:** Python 3.12 (tested)
- **Tested:** CPython and PyPy

### Recommendations

#### Short Term (Next Release)
- ✅ **Keep Python 3.9+ requirement** (good balance)
- ✅ Add Python 3.13 testing to CI
- Document Python 3.13 compatibility

#### Medium Term (6-12 months)
- Consider raising minimum to Python 3.10
  - Benefits: Better type hints, match statements, better error messages
  - Drawback: Drops Python 3.9 users (EOL: October 2025)
- Add Python 3.14 testing when available

#### Long Term (12+ months)
- Python 3.9 reaches EOL in October 2025
- Plan migration to Python 3.10+ by Q4 2025
- Leverage newer features: Pattern matching, improved type hints

---

## 🚀 Code Modernization Opportunities

### 1. Async Event Loop Warning Fix
**Current Issue:** DeprecationWarning in `rate_limiter.py:35`
```python
self._loop = asyncio.get_event_loop()
```

**Recommendation:**
```python
# Replace with:
try:
    self._loop = asyncio.get_running_loop()
except RuntimeError:
    self._loop = asyncio.new_event_loop()
    asyncio.set_event_loop(self._loop)
```

### 2. Type Hints Enhancement
- Consider using `typing_extensions.Self` for method chaining
- Add more generic type parameters where applicable
- Use newer union syntax `X | Y` when dropping Python 3.9

### 3. Performance Optimizations
- Profile hot paths in request/response handling
- Consider caching compiled URL templates
- Optimize proxy merging logic

### 4. Documentation Improvements
- Add more inline examples
- Create migration guide from v0.x to v1.x
- Document httpx auth support (newly added)
- Add troubleshooting section

---

## 📋 Implementation Roadmap

### Phase 1: Immediate (Week 1)
- [x] Fix proxy configuration bug
- [x] Add httpx auth support
- [ ] Update httpx to 0.28.x
- [ ] Update pydantic to 2.12.x
- [ ] Fix async event loop warning
- [ ] Run full test suite
- [ ] Update CHANGELOG.md

### Phase 2: Near Term (Month 1)
- [ ] Update mypy to 1.19.x
- [ ] Update pytest-xdist and pytest-mock
- [ ] Add Python 3.13 to CI matrix
- [ ] Update documentation with new auth features
- [ ] Set up automated dependency scanning

### Phase 3: Medium Term (Quarter 1)
- [ ] Evaluate pytest 8.x upgrade
- [ ] Evaluate pylint 4.x upgrade
- [ ] Evaluate flake8 7.x upgrade
- [ ] Performance profiling and optimization
- [ ] Create migration guide

### Phase 4: Long Term (6-12 months)
- [ ] Plan Python 3.10 minimum version bump
- [ ] Evaluate pytest 9.x upgrade
- [ ] Consider async/await improvements
- [ ] Explore HTTP/3 support (when stable)

---

## ✅ Testing Strategy

### Before Each Update
1. Run all linters: `make flake8 pylint mypy`
2. Run full test suite: `make pytest`
3. Check coverage: `pytest --cov`
4. Run security scan: `pip-audit` or `safety check`

### After Each Update
1. Verify all tests pass
2. Check for deprecation warnings
3. Review code quality scores
4. Update documentation if needed
5. Test in isolation environment

### Continuous Integration
- Run tests on all supported Python versions
- Run linters on every commit
- Generate coverage reports
- Fail on coverage decrease

---

## 🎯 Success Metrics

### Quality Metrics
- ✅ Maintain 100% test coverage
- ✅ Maintain 10.0/10.0 pylint score
- ✅ Zero mypy errors
- ✅ Zero flake8 violations

### Performance Metrics
- Maintain current request/response latency
- Keep package size < 200KB
- Keep dependencies minimal (< 10 direct deps)

### Security Metrics
- Zero known vulnerabilities
- All dependencies < 6 months old
- Regular security audits (quarterly)

---

## 📝 Notes

### Breaking Changes to Avoid
- Don't change public API signatures
- Maintain backward compatibility with Auth classes
- Keep minimum Python version stable for 1.x releases

### Future Considerations
- GraphQL client improvements
- WebSocket support
- Server-Sent Events (SSE) support
- gRPC support consideration
- OpenAPI/Swagger code generation

---

## 🤝 Contributing

For questions or suggestions about this upgrade plan:
1. Open an issue on GitHub
2. Tag with `dependencies` or `enhancement`
3. Reference this UPGRADE_PLAN.md

---

**Last Updated:** 2026-02-15  
**Next Review:** 2026-05-15 (Quarterly)
