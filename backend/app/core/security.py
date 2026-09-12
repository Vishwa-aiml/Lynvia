"""Core security module.

Authentication is now handled by app.api.dependencies (get_current_user, etc.)
and app.utils.security (JWT encode/decode).

This module is kept minimal for backward compatibility.
"""
