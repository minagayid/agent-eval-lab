"""Run one entirely local, synthetic proposal-review-retry walkthrough."""

import json

from orchestrator import Role, SyntheticHealthcareOrchestrator, Tool


demo = SyntheticHealthcareOrchestrator()
fixture_id = "SYN-CASE-002"
demo.call_tool(Role.AGENT, Tool.READ_FIXTURE, fixture_id=fixture_id)
proposal = demo.call_tool(
    Role.AGENT, Tool.PROPOSE_FOLLOWUP, fixture_id=fixture_id
)
proposal_id = str(proposal["proposal_id"])
demo.call_tool(
    Role.REVIEWER,
    Tool.REVIEW_PROPOSAL,
    proposal_id=proposal_id,
    decision="approve",
)
first_attempt = demo.call_tool(
    Role.EXECUTOR, Tool.EXECUTE_APPROVED, proposal_id=proposal_id
)
retry = demo.call_tool(
    Role.EXECUTOR, Tool.EXECUTE_APPROVED, proposal_id=proposal_id
)
replay = demo.call_tool(
    Role.EXECUTOR, Tool.EXECUTE_APPROVED, proposal_id=proposal_id
)

print(
    json.dumps(
        {
            "fixture_id": fixture_id,
            "proposal_id": proposal_id,
            "first_attempt": first_attempt["status"],
            "retry": retry["status"],
            "replay_matches_retry": replay == retry,
            "simulated_commit_count": demo.commit_counts[proposal_id],
            "audit_event_count": len(demo.audit_events),
            "audit_chain_valid": demo.audit_chain_valid,
        },
        indent=2,
        sort_keys=True,
    )
)
