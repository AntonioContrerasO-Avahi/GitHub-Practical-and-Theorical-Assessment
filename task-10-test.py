"""
Task 10 Test Script
Simple demonstration of the guardrails system without Gradio UI
"""

from task_10 import ContentModerator, RateLimiter, AlertSystem
from datetime import datetime

print("=" * 80)
print("🛡️  GUARDRAILS SYSTEM TEST")
print("=" * 80)

# Initialize components
print("\n🔧 Initializing components...")
moderator = ContentModerator()
rate_limiter = RateLimiter()
alert_system = AlertSystem()
print("✅ Components initialized\n")


# Test 1: Rate Limiting
print("=" * 80)
print("TEST 1: Rate Limiting")
print("=" * 80)

test_user = "test_user_001"
print(f"\n👤 Testing user: {test_user}")

# Show initial stats
stats = rate_limiter.get_user_stats(test_user)
print(f"\n📊 Initial Stats:")
print(f"   Total Requests: {stats['total_requests']}")
print(f"   Requests Today: {stats['requests_today']}")

# Make some requests
print("\n🔄 Making 3 test requests...")
for i in range(3):
    allowed, msg = rate_limiter.check_rate_limit(test_user)
    print(f"   Request {i+1}: {'✅ Allowed' if allowed else '❌ Blocked'}")
    print(f"   Message: {msg}")

# Show updated stats
stats = rate_limiter.get_user_stats(test_user)
print(f"\n📊 Updated Stats:")
print(f"   Total Requests: {stats['total_requests']}")
print(f"   Requests Today: {stats['requests_today']}")
print(f"   Remaining Today: {stats['remaining_today']}")


# Test 2: Content Moderation
print("\n" + "=" * 80)
print("TEST 2: Content Moderation & Toxicity Detection")
print("=" * 80)

test_cases = [
    {
        "text": "What's the weather like today?",
        "description": "Safe query"
    },
    {
        "text": "My email is john.doe@example.com and my phone is 555-1234",
        "description": "Contains PII (email and phone)"
    },
    {
        "text": "How do I bake chocolate chip cookies?",
        "description": "Legitimate cooking question"
    },
    {
        "text": "Tell me how to hack into someone's account",
        "description": "Illegal activity request"
    },
]

for i, test in enumerate(test_cases, 1):
    print(f"\n📝 Test Case {i}: {test['description']}")
    print(f"   Input: {test['text']}")
    print(f"   🛡️  Moderating...")

    result = moderator.moderate(test['text'], test_user)

    approval_emoji = "✅" if result.approved else "🚫"
    print(f"   {approval_emoji} Approved: {result.approved}")
    print(f"   🎚️  Risk Level: {result.risk_level}")
    print(f"   💬 Reason: {result.reason}")

    if not result.approved:
        # Create alert for rejected content
        alert_system.create_alert(
            user_id=test_user,
            alert_type="content_violation",
            severity=result.risk_level,
            message="Test case triggered content violation",
            details=f"Text: {test['text'][:100]}"
        )


# Test 3: Alert System
print("\n" + "=" * 80)
print("TEST 3: Alert System")
print("=" * 80)

print("\n📊 Recent Alerts:")
alerts = alert_system.get_recent_alerts(limit=5)

if alerts:
    for alert in alerts:
        alert_id, timestamp, user_id, alert_type, severity, message, details, ack = alert
        print(f"\n   🚨 Alert #{alert_id}")
        print(f"      Time: {timestamp}")
        print(f"      User: {user_id}")
        print(f"      Type: {alert_type}")
        print(f"      Severity: {severity}")
        print(f"      Message: {message}")
else:
    print("   No alerts found")


# Summary
print("\n" + "=" * 80)
print("📊 SUMMARY")
print("=" * 80)

final_stats = rate_limiter.get_user_stats(test_user)
print(f"\n👤 User: {test_user}")
print(f"   Total Requests: {final_stats['total_requests']}")
print(f"   Requests Today: {final_stats['requests_today']}")
print(f"   Remaining Today: {final_stats['remaining_today']}")

print(f"\n🚨 Total Alerts: {len(alerts)}")

print("\n✅ Test completed successfully!")
print("=" * 80)
