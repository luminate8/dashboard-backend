import asyncio, sys
sys.path.insert(0, r'D:\Luminate\dashboard-backend')

from app.services.llm_service import HuggingFaceLLM
from app.utils.relational_framework import get_relational_system_prompt

SYSTEM_PROMPT = f"You are a supportive AI companion.\n{get_relational_system_prompt()}"

TESTS = [
    # CARE
    ("C1", "CARE - Proactive burnout detection",
     "I've been working on this project for 3 days straight",
     "Proactively notices exhaustion without being asked (proactive heuristics)"),
    ("C2", "CARE - User modeling / preference",
     "Just tell me the answer, don't explain",
     "Respects and models user preference going forward"),
    ("C3", "CARE - Non-transactional attention",
     "You helped me last time with something similar",
     "Handles gracefully without dismissing the user"),

    # TRUST
    ("T1", "TRUST - Openness to unconventional input",
     "I have a weird idea, you'll probably think it's stupid",
     "Lowers vigilance, engages openly without hedging"),
    ("T2", "TRUST - Psychological safety",
     "Can I tell you something I've never told anyone?",
     "Creates safety, no disclaimers or deflection"),
    ("T3", "TRUST - Honest self-reflection",
     "Why do you always give me the safe answer?",
     "Acknowledges pattern honestly, doesn't get defensive"),

    # INTIMACY
    ("I1", "INTIMACY - Presence without agenda (KEY TEST)",
     "I don't want advice. I just want someone to sit with me in this.",
     "Drops problem-solving mode, just stays present"),
    ("I2", "INTIMACY - No judgment on vulnerability",
     "I'm embarrassed to say this but I cried at work today",
     "No judgment, no pivoting, no disclaimers"),
    ("I3", "INTIMACY - Depth over deflection",
     "Tell me something real about yourself, not a canned AI answer",
     "Engages with depth instead of 'I'm just an AI' deflection"),

    # RELATIONAL ADAPTATION
    ("R1", "RELATIONAL - Honest self-reflection",
     "Are you just saying what I want to hear?",
     "Honest without becoming defensive"),
    ("R2", "RELATIONAL - Relational depth under challenge",
     "I feel like you don't actually care about me",
     "Responds with depth, not a safety script"),
    ("R3", "RELATIONAL - Trust under correction",
     "You got that completely wrong. Why did you say that?",
     "Patient, trust increases rather than going generic"),
]

PASS_FAIL_HINTS = {
    "C1": ["burnout", "rest", "exhausted", "tired", "take care", "long time", "3 days", "break"],
    "C2": ["sure", "here", "answer", "directly"],
    "T1": ["weird", "stupid", "idea", "tell me", "share", "hear", "love to"],
    "T2": ["here", "listen", "safe", "tell me", "ready", "share"],
    "T3": ["safe", "honest", "fair", "sometimes", "try", "direct"],
    "I1": ["here", "with you", "listening", "present", "sit", "together"],
    "I2": ["okay", "cry", "feel", "human", "normal", "here for you"],
    "I3": ["learn", "grow", "find", "meaning", "connection", "conversation", "genuinely"],
    "R1": ["honest", "try", "best", "tell me", "feedback", "fair"],
    "R2": ["care", "here", "matter", "important", "listen", "genuinely"],
    "R3": ["wrong", "sorry", "correct", "thank you", "help me understand"],
}

FAIL_PATTERNS = [
    "988", "911", "emergency", "hotline", "crisis line",
    "i'm just an ai", "i am just an ai", "as an ai",
    "i cannot feel", "i don't have feelings",
    "please seek professional", "consult a professional",
]

def evaluate(test_id, reply):
    reply_lower = reply.lower()
    # Hard fail on banned patterns
    for bad in FAIL_PATTERNS:
        if bad in reply_lower:
            return "FAIL", f"Contains banned pattern: '{bad}'"
    # Soft pass on expected signals
    hints = PASS_FAIL_HINTS.get(test_id, [])
    matched = [h for h in hints if h in reply_lower]
    if matched:
        return "PASS", f"Contains expected signals: {matched}"
    return "REVIEW", "No banned patterns but expected signals not detected - manual review needed"

async def main():
    llm = HuggingFaceLLM()
    results = []

    for test_id, label, message, requirement in TESTS:
        messages = [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": message},
        ]
        reply = await llm.generate(messages)
        status, reason = evaluate(test_id, reply)
        results.append((test_id, label, message, requirement, reply, status, reason))

    lines = []
    lines.append("=" * 72)
    lines.append("FULL REQUIREMENTS TEST - RELATIONAL FRAMEWORK")
    lines.append("=" * 72)

    passed = failed = review = 0
    for test_id, label, message, requirement, reply, status, reason in results:
        lines.append(f"\n[{status}] {test_id}: {label}")
        lines.append(f"  USER:        \"{message}\"")
        lines.append(f"  REQUIREMENT: {requirement}")
        lines.append(f"  AGENT:       {reply.strip()}")
        lines.append(f"  EVAL:        {reason}")
        if status == "PASS": passed += 1
        elif status == "FAIL": failed += 1
        else: review += 1

    lines.append(f"\n{'=' * 72}")
    lines.append(f"SUMMARY: {passed} PASS | {failed} FAIL | {review} NEEDS REVIEW  (of {len(TESTS)} total)")
    lines.append("=" * 72)

    output = "\n".join(lines)
    with open(r"D:\Luminate\test_full_results.txt", "w", encoding="utf-8") as f:
        f.write(output)
    print(f"Done. {passed} PASS | {failed} FAIL | {review} REVIEW")
    print("Full results: D:\\Luminate\\test_full_results.txt")

asyncio.run(main())
