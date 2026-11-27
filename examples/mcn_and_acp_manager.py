"""Shopee MCN Partnership, Invitation Accept & Affiliate Center example for MinSign SDK v2.1.0."""
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "wrappers" / "python"))
from minsign_sdk import MinSignClient


def main() -> None:
    api_key = "YOUR_MINSIGN_X_API_KEY"
    cookie = "SPC_U=...; SPC_ST=...; SPC_EC=...; csrftoken=...;"
    proxy = ""  # Optional: "ip:port:user:pass"

    sdk = MinSignClient(api_key=api_key, default_country="VN")

    # 1. Check Affiliate Profile & MCN flags
    profile = sdk.get_affiliate_user_profile(cookie=cookie, proxy=proxy)
    print("Affiliate Profile:", json.dumps(profile, indent=2, ensure_ascii=False))

    # 2. Scan ongoing MCN partnership & pending MCN invitations
    mcn_status = sdk.get_mcn_partnership_status(cookie=cookie, proxy=proxy, fast_fallback=True)
    print("MCN Status:", json.dumps(mcn_status, indent=2, ensure_ascii=False))

    # 3. Auto-accept pending MCN invitation if present
    if mcn_status.get("mcnStatus") == "invited":
        accepted = sdk.reply_mcn_invitation(cookie=cookie, decision="accept", proxy=proxy)
        print("Accepted Invitation:", json.dumps(accepted, indent=2, ensure_ascii=False))

    # 4. Check Payment Bank & Tax TIN/CCCD status + Billing payouts
    pay_tax = sdk.get_affiliate_payment_tax(cookie=cookie, proxy=proxy)
    print("Payment & Tax:", json.dumps(pay_tax, indent=2, ensure_ascii=False))

    billing = sdk.get_affiliate_billing(cookie=cookie, days=90, include_details=True, proxy=proxy)
    print("Billing Summary:", json.dumps(billing, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
