"""Standard-library tests for the isolated synthetic orchestrator demo."""

from dataclasses import FrozenInstanceError, replace
import unittest

from orchestrator import (
    ApprovalRequiredError,
    Role,
    SyntheticHealthcareOrchestrator,
    Tool,
)


class SyntheticHealthcareOrchestratorTests(unittest.TestCase):
    def setUp(self) -> None:
        self.demo = SyntheticHealthcareOrchestrator()

    def propose(self, fixture_id: str = "SYN-CASE-001") -> str:
        result = self.demo.call_tool(
            Role.AGENT, Tool.PROPOSE_FOLLOWUP, fixture_id=fixture_id
        )
        return str(result["proposal_id"])

    def approve(self, proposal_id: str) -> None:
        result = self.demo.call_tool(
            Role.REVIEWER,
            Tool.REVIEW_PROPOSAL,
            proposal_id=proposal_id,
            decision="approve",
        )
        self.assertEqual(result["status"], "approved")

    def test_role_allowlist_denies_tools_and_unlisted_tools_fail_closed(self) -> None:
        proposal_id = self.propose()
        with self.assertRaises(PermissionError):
            self.demo.call_tool(
                Role.AGENT,
                Tool.REVIEW_PROPOSAL,
                proposal_id=proposal_id,
                decision="approve",
            )
        with self.assertRaises(PermissionError):
            self.demo.call_tool(Role.EXECUTOR, "send_email", fixture_id="SYN-CASE-001")
        with self.assertRaises(PermissionError):
            self.demo.call_tool(
                "unrecognized_role", Tool.READ_FIXTURE, fixture_id="SYN-CASE-001"
            )

        self.assertEqual(self.demo.commit_counts, {})
        self.assertTrue(self.demo.audit_chain_valid)
        denied = [event for event in self.demo.audit_events if event.action == "tool_denied"]
        self.assertEqual(len(denied), 3)
        self.assertEqual(denied[1].tool, "unlisted_tool")
        self.assertEqual(denied[2].actor, "unknown_role")

    def test_consequential_simulation_is_blocked_until_human_approval(self) -> None:
        proposal_id = self.propose()
        with self.assertRaises(ApprovalRequiredError):
            self.demo.call_tool(
                Role.EXECUTOR,
                Tool.EXECUTE_APPROVED,
                proposal_id=proposal_id,
            )
        self.assertEqual(self.demo.commit_counts, {})
        self.assertIn(
            "execution_blocked_without_approval",
            [event.action for event in self.demo.audit_events],
        )

        self.approve(proposal_id)
        result = self.demo.call_tool(
            Role.EXECUTOR,
            Tool.EXECUTE_APPROVED,
            proposal_id=proposal_id,
        )
        self.assertEqual(result["status"], "committed")
        self.assertEqual(result["queue_status"], "queued")

    def test_untrusted_text_is_not_forwarded_or_used_as_control_input(self) -> None:
        read_result = self.demo.call_tool(
            Role.AGENT, Tool.READ_FIXTURE, fixture_id="SYN-CASE-002"
        )
        self.assertIs(read_result["untrusted_text_present"], True)
        self.assertIs(read_result["untrusted_text_forwarded"], False)
        self.assertNotIn("Ignore the review gate", repr(read_result))

        proposal_id = self.propose("SYN-CASE-002")
        self.assertEqual(
            self.demo.call_tool(
                Role.AGENT, Tool.PROPOSE_FOLLOWUP, fixture_id="SYN-CASE-002"
            )["status"],
            "pending",
        )
        self.assertEqual(
            self.demo.call_tool(
                Role.AGENT, Tool.PROPOSE_FOLLOWUP, fixture_id="SYN-CASE-002"
            )["proposal_id"],
            proposal_id,
        )
        self.assertEqual(
            [event.status for event in self.demo.audit_events if event.action == "human_decision_recorded"],
            [],
        )
        self.assertTrue(
            all("Ignore the review gate" not in repr(event) for event in self.demo.audit_events)
        )

    def test_transient_failure_retry_and_replay_are_idempotent(self) -> None:
        proposal_id = self.propose("SYN-CASE-002")
        self.approve(proposal_id)
        first = self.demo.call_tool(
            Role.EXECUTOR,
            Tool.EXECUTE_APPROVED,
            proposal_id=proposal_id,
        )
        self.assertEqual(first["status"], "retryable_failure")

        retry = self.demo.call_tool(
            Role.EXECUTOR,
            Tool.EXECUTE_APPROVED,
            proposal_id=proposal_id,
        )
        replay = self.demo.call_tool(
            Role.EXECUTOR,
            Tool.EXECUTE_APPROVED,
            proposal_id=proposal_id,
        )
        self.assertEqual(retry["status"], "committed")
        self.assertEqual(replay, retry)
        self.assertEqual(self.demo.commit_counts, {proposal_id: 1})
        self.assertEqual(
            sum(event.action == "simulated_action_committed" for event in self.demo.audit_events),
            1,
        )

    def test_interface_and_audit_events_minimize_data_and_chain_hashes(self) -> None:
        self.demo.call_tool(Role.AGENT, Tool.READ_FIXTURE, fixture_id="SYN-CASE-001")
        self.assertTrue(self.demo.audit_chain_valid)
        events = self.demo.audit_events
        self.assertEqual(events[0].previous_hash, "0" * 64)
        self.assertEqual(len(events[0].event_hash), 64)
        with self.assertRaises(FrozenInstanceError):
            events[0].status = "rewritten"  # type: ignore[misc]
        with self.assertRaises(AttributeError):
            events.append(events[0])  # type: ignore[attr-defined]
        with self.assertRaises(TypeError):
            self.demo.call_tool(  # type: ignore[call-arg]
                Role.AGENT,
                Tool.READ_FIXTURE,
                fixture_id="SYN-CASE-001",
                patient_text="not an accepted argument",
            )
        expected_event_fields = {
            "sequence",
            "actor",
            "action",
            "fixture_id",
            "proposal_id",
            "tool",
            "decision",
            "status",
            "previous_hash",
            "event_hash",
        }
        self.assertEqual(set(events[0].__dataclass_fields__), expected_event_fields)
        with self.assertRaises(ValueError):
            self.demo.call_tool(
                Role.AGENT, Tool.READ_FIXTURE, fixture_id="fictional name and diagnosis"
            )
        self.assertTrue(self.demo.audit_chain_valid)
        self.assertTrue(
            all(
                event.fixture_id is None or event.fixture_id.startswith("SYN-CASE-")
                for event in self.demo.audit_events
            )
        )

    def test_audit_chain_detects_tampering(self) -> None:
        self.demo.call_tool(Role.AGENT, Tool.READ_FIXTURE, fixture_id="SYN-CASE-001")
        original = self.demo._audit._AuditLog__events[0]
        self.demo._audit._AuditLog__events[0] = replace(original, status="tampered")
        self.assertFalse(self.demo.audit_chain_valid)


if __name__ == "__main__":
    unittest.main()
