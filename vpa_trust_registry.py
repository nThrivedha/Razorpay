"""
BeforePay — VPA / Payee Trust Score Registry
-----------------------------------------------
Razorpay AI Risk Manager — Track 02: AI Risk Manager

Maintains three-tier payee reputation:
  TRUSTED   (0.0) — Verified merchant escrow handles (Swiggy, Zomato, BigBasket, etc.)
  UNKNOWN   (0.5) — Never-seen VPA with no negative signals
  WATCHLIST (1.0) — Previously flagged mule VPA (auto-added on HARD_INTERCEPT)

Closes the documented False Positive case:
  User buying a used car via verified escrow handle — now score drops from HIGH → MEDIUM
  because the escrow VPA resolves to TRUSTED tier.
"""

import threading
from datetime import datetime


# ──────────────────────────────────────────────────────────────────
# Seed dataset: real-world merchant handle patterns that Razorpay
# Route / NPCI verified merchants typically use
# ──────────────────────────────────────────────────────────────────
_TRUSTED_PATTERNS = [
    # Food & Grocery delivery
    "swiggy", "zomato", "bigbasket", "grofers", "blinkit", "zepto",
    # E-commerce
    "amazon", "flipkart", "meesho", "myntra", "ajio", "snapdeal",
    # Utilities
    "bsnl", "jio", "airtel", "vodafone", "idea", "tatapower", "adani.elec",
    # Transport
    "ola", "uber", "rapido", "irctc", "makemytrip", "goibibo",
    # Finance / Insurance
    "paytmmall", "phonepe.merchant", "googlepay.merchant",
    "licindia", "hdfclife", "iciciprudential",
    # Government
    "gov.in", "uidai", "npci", "bbps",
    # Verified escrow patterns (OLX, Cars24, Spinny, Droom)
    "cars24.escrow", "olx.escrow", "spinny.escrow", "droom.escrow",
    "classifieds.escrow", "marketplace.escrow",
]

# VPA suffixes that are inherently suspicious (disposable / mule handles)
_SUSPICIOUS_SUFFIXES = [
    "@cybercell", "@ybl_temp", "@temp_upi", "@scam_relay",
]

# Known-bad exact VPA fragments loaded from prior intercepts
_KNOWN_MULE_FRAGMENTS = [
    "rbi.verify", "cbi.freeze", "customs.verify", "fake.helpline",
    "refund.desk", "verification_fee", "bail.advocates",
    "emergency.bail", "fast.settle", "crypto.escrow.relay",
    "offramp.cashout", "otp.verify", "kyc.suspend", "reward.claim",
]


class VPATrustRegistry:
    """
    Thread-safe, in-memory VPA trust registry with automatic watchlist promotion.

    Usage:
        registry = VPATrustRegistry()
        result = registry.lookup("swiggy_order_pay@icici")
        # → {"trust_tier": "TRUSTED", "trust_score": 0.0, "reason": "Verified merchant pattern"}

        registry.flag_as_mule("rbi.verify.mule_25@cybercell", reason="HARD_INTERCEPT action")
    """

    TRUSTED = "TRUSTED"
    UNKNOWN = "UNKNOWN"
    WATCHLIST = "WATCHLIST"

    def __init__(self):
        self._lock = threading.Lock()
        # vpa → {"trust_tier", "trust_score", "reason", "flagged_at"}
        self._watchlist: dict[str, dict] = {}
        self._trusted_overrides: dict[str, dict] = {}
        self._lookup_cache: dict[str, dict] = {}

    # ──────────────────────────────────────────────
    # Public API
    # ──────────────────────────────────────────────

    def lookup(self, vpa: str) -> dict:
        """
        Returns trust assessment for a given VPA string.
        Result keys: trust_tier, trust_score (0.0–1.0), reason, vpa
        """
        if not vpa:
            return self._build_result(vpa, self.UNKNOWN, 0.5, "Empty VPA")

        vpa_lower = vpa.lower().strip()

        with self._lock:
            # 1. Check cache
            if vpa_lower in self._lookup_cache:
                return self._lookup_cache[vpa_lower]

            result = self._classify(vpa_lower)
            self._lookup_cache[vpa_lower] = result
            return result

    def flag_as_mule(self, vpa: str, reason: str = "Flagged by BeforePay") -> None:
        """
        Adds a VPA to the persistent mule watchlist.
        Called automatically by ml_models.py on every HARD_INTERCEPT action.
        """
        if not vpa:
            return
        vpa_lower = vpa.lower().strip()
        with self._lock:
            self._watchlist[vpa_lower] = {
                "trust_tier": self.WATCHLIST,
                "trust_score": 1.0,
                "reason": f"Auto-flagged: {reason}",
                "flagged_at": datetime.now().isoformat()
            }
            # Invalidate cache entry
            self._lookup_cache.pop(vpa_lower, None)

    def add_trusted(self, vpa: str, reason: str = "Manually verified") -> None:
        """Manually adds a VPA to the trusted tier (e.g., merchant onboarding)."""
        if not vpa:
            return
        vpa_lower = vpa.lower().strip()
        with self._lock:
            self._trusted_overrides[vpa_lower] = {
                "trust_tier": self.TRUSTED,
                "trust_score": 0.0,
                "reason": reason,
            }
            self._lookup_cache.pop(vpa_lower, None)

    def get_watchlist(self) -> list[dict]:
        """Returns all VPAs currently on the mule watchlist."""
        with self._lock:
            return [
                {"vpa": vpa, **info}
                for vpa, info in self._watchlist.items()
            ]

    def watchlist_size(self) -> int:
        with self._lock:
            return len(self._watchlist)

    # ──────────────────────────────────────────────
    # Internal Classification Logic
    # ──────────────────────────────────────────────

    def _classify(self, vpa_lower: str) -> dict:
        # Priority 1: Explicit watchlist (highest precedence)
        if vpa_lower in self._watchlist:
            entry = self._watchlist[vpa_lower]
            return self._build_result(vpa_lower, self.WATCHLIST, 1.0, entry["reason"])

        # Priority 2: Known mule VPA fragments
        for fragment in _KNOWN_MULE_FRAGMENTS:
            if fragment in vpa_lower:
                return self._build_result(
                    vpa_lower, self.WATCHLIST, 1.0,
                    f"Known mule pattern: '{fragment}'"
                )

        # Priority 3: Suspicious suffixes
        for suffix in _SUSPICIOUS_SUFFIXES:
            if vpa_lower.endswith(suffix):
                return self._build_result(
                    vpa_lower, self.WATCHLIST, 0.9,
                    f"Suspicious handle suffix: '{suffix}'"
                )

        # Priority 4: Explicit trusted overrides
        if vpa_lower in self._trusted_overrides:
            entry = self._trusted_overrides[vpa_lower]
            return self._build_result(vpa_lower, self.TRUSTED, 0.0, entry["reason"])

        # Priority 5: Known trusted merchant patterns
        for pattern in _TRUSTED_PATTERNS:
            if pattern in vpa_lower:
                return self._build_result(
                    vpa_lower, self.TRUSTED, 0.0,
                    f"Verified merchant pattern: '{pattern}'"
                )

        # Default: Unknown
        return self._build_result(vpa_lower, self.UNKNOWN, 0.5, "No prior signal")

    @staticmethod
    def _build_result(vpa: str, tier: str, score: float, reason: str) -> dict:
        return {
            "vpa": vpa,
            "trust_tier": tier,
            "trust_score": round(score, 2),
            "reason": reason,
        }


# Module-level singleton — imported and shared across ml_models.py
_registry_instance: VPATrustRegistry | None = None


def get_registry() -> VPATrustRegistry:
    """Returns the module-level singleton VPATrustRegistry."""
    global _registry_instance
    if _registry_instance is None:
        _registry_instance = VPATrustRegistry()
    return _registry_instance


if __name__ == "__main__":
    reg = VPATrustRegistry()

    test_vpas = [
        "swiggy_order_pay@icici",
        "rbi.verify.mule_25@cybercell",
        "emergency.bail.advocates@axis",
        "cars24.escrow.txn@hdfc",
        "priyasharma45@pnb",           # unknown personal VPA
        "merchant_6@icici",             # unknown merchant
    ]

    print("=== VPA Trust Registry Lookup Results ===")
    for vpa in test_vpas:
        result = reg.lookup(vpa)
        tier_symbol = {"TRUSTED": "✅", "UNKNOWN": "❓", "WATCHLIST": "🚨"}[result["trust_tier"]]
        print(f"  {tier_symbol} {vpa:<45} → {result['trust_tier']:<10} (score={result['trust_score']}) [{result['reason']}]")

    print("\n[+] Auto-flagging 'scammer.relay@ybl_temp' via HARD_INTERCEPT...")
    reg.flag_as_mule("scammer.relay@ybl_temp", reason="HARD_INTERCEPT on pay_scam_999")
    result = reg.lookup("scammer.relay@ybl_temp")
    print(f"  Re-lookup: {result['trust_tier']} — {result['reason']}")
    print(f"\nWatchlist size: {reg.watchlist_size()} entries")
