#!/usr/bin/env python3
"""Repository lint dispatcher and legacy raw/authored leaf regression tests."""
from __future__ import annotations

import importlib.util
import io
import os
import shutil
import sys
import tempfile
from contextlib import redirect_stdout
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
LINT_PATH = REPO_ROOT / "scripts" / "lint.py"


def _load_lint_module():
    spec = importlib.util.spec_from_file_location("wiki_lint", LINT_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot load lint module: {LINT_PATH}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


lint = _load_lint_module()
REFERENCE_PATH = REPO_ROOT / "wiki" / "domains" / "test" / "reference.md"
TESTS = []


def _register(fn):
    TESTS.append(fn)
    return fn


@_register
def test_broken_link_check_rejects_missing_target():
    findings = lint.check_axis_5_integrity_broken_links(
        REFERENCE_PATH,
        "[[wiki/domains/does-not-exist/overview]]",
    )

    assert any("broken link" in finding.message for finding in findings)


@_register
def test_wikilink_resolver_tries_repo_root_and_strips_heading():
    for link in ("[[AGENTS.md]]", "[[AGENTS.md#Mission]]"):
        assert lint.check_axis_5_integrity_broken_links(REFERENCE_PATH, link) == []


@_register
def test_directory_link_requires_overview_or_index():
    findings = lint.check_axis_5_integrity_broken_links(
        REFERENCE_PATH,
        "[[wiki/domains/information-security]]",
    )

    assert any("broken link" in finding.message for finding in findings)


@_register
def test_content_addressed_artifact_markdown_is_not_a_legacy_raw_page():
    payloads = sorted(
        (REPO_ROOT / "raw" / "sources" / "clipping").glob("*/*/payload.md")
    )

    assert payloads
    assert all(lint.is_artifact_bundle_markdown(payload) for payload in payloads)
    markdown_paths, findings = lint._markdown_inventory(payloads)
    assert markdown_paths == []
    assert findings == []


@_register
def test_flat_curated_raw_markdown_remains_in_legacy_lint_scope():
    pages = sorted((REPO_ROOT / "raw" / "sources" / "web").rglob("*.md"))
    # raw/sources/web holds both flat curated pages and content-addressed bundles.
    # Select by path shape so the assertion stays about the flat leaf either way.
    flat = [
        page
        for page in pages
        if len(page.relative_to(REPO_ROOT).parts) == 5
    ]

    assert flat
    assert not lint.is_artifact_bundle_markdown(flat[0])
    markdown_paths, findings = lint._markdown_inventory([flat[0]])
    assert markdown_paths == [flat[0]]
    assert findings == []


@_register
def test_repository_lint_paths_share_the_default_inventory_owner():
    candidates = [
        REPO_ROOT / "wiki" / "page.md",
        REPO_ROOT / "raw" / "source.md",
        REPO_ROOT / "_meta" / "contract.md",
        REPO_ROOT / "AGENTS.md",
        REPO_ROOT / "docs" / "design.md",
        REPO_ROOT / "README.md",
    ]

    assert lint.default_repository_paths() == [
        lint.WIKI_DIR,
        REPO_ROOT / "raw",
        lint.META_DIR,
        REPO_ROOT / "AGENTS.md",
    ]
    assert lint.repository_lint_paths(candidates) == candidates[:4]


@_register
def test_repository_lint_paths_normalize_dot_segments_before_scope_selection():
    candidates = [
        REPO_ROOT / "raw" / ".." / "docs" / "design.md",
        REPO_ROOT / "raw" / ".." / "raw" / "source.md",
        REPO_ROOT / "wiki" / ".." / ".." / "outside.md",
    ]

    assert lint.repository_lint_paths(candidates) == [
        (REPO_ROOT / "raw" / "source.md").resolve(strict=False)
    ]


@_register
def test_repository_lint_paths_reject_scope_symlink_that_resolves_outside_repository():
    with tempfile.TemporaryDirectory() as outside_directory:
        outside = Path(outside_directory)
        with tempfile.TemporaryDirectory(dir=REPO_ROOT / "raw") as directory:
            link = Path(directory) / "external"
            link.symlink_to(outside, target_is_directory=True)
            candidate = link / "source.md"

            assert lint.repository_lint_paths([candidate]) == []


@_register
def test_repository_lint_paths_preserve_internal_symlink_leaf_for_inventory_rejection():
    with tempfile.TemporaryDirectory(dir=REPO_ROOT / "raw") as directory:
        root = Path(directory)
        target = root / "target.md"
        target.write_text("# target\n", encoding="utf-8")
        link = root / "link.md"
        link.symlink_to(target)

        selected = lint.repository_lint_paths([link])
        findings = lint.collect_findings(selected)

        assert selected == [link]
        assert any(
            finding.severity == "HIGH"
            and finding.path == link
            and "symbolic links" in finding.message
            for finding in findings
        )


@_register
def test_repository_lint_paths_preserve_external_symlink_leaf_for_inventory_rejection():
    with tempfile.TemporaryDirectory() as outside_directory:
        target = Path(outside_directory) / "target.md"
        target.write_text("# target\n", encoding="utf-8")
        with tempfile.TemporaryDirectory(dir=REPO_ROOT / "raw") as directory:
            link = Path(directory) / "link.md"
            link.symlink_to(target)

            selected = lint.repository_lint_paths([link])
            findings = lint.collect_findings(selected)

            assert selected == [link]
            assert any(
                finding.severity == "HIGH"
                and finding.path == link
                and "symbolic links" in finding.message
                for finding in findings
            )


@_register
def test_repository_lint_paths_preserve_single_file_scope_symlink_for_inventory_rejection():
    original_defaults = lint.default_repository_paths
    with tempfile.TemporaryDirectory(dir=REPO_ROOT) as directory:
        root = Path(directory)
        for scope in ("wiki", "raw", "_meta"):
            (root / scope).mkdir()
        internal_target = root / "directive.md"
        internal_target.write_text("# target\n", encoding="utf-8")
        with tempfile.TemporaryDirectory() as outside_directory:
            external_target = Path(outside_directory) / "directive.md"
            external_target.write_text("# target\n", encoding="utf-8")
            try:
                for target in (internal_target, external_target):
                    agents = root / "AGENTS.md"
                    agents.symlink_to(target)
                    lint.default_repository_paths = lambda: [
                        root / "wiki",
                        root / "raw",
                        root / "_meta",
                        agents,
                    ]

                    selected = lint.repository_lint_paths([agents])
                    findings = lint.collect_findings(selected)

                    assert selected == [agents]
                    assert any(
                        finding.severity == "HIGH"
                        and finding.path == agents
                        and "symbolic links" in finding.message
                        for finding in findings
                    )
                    agents.unlink()
            finally:
                lint.default_repository_paths = original_defaults


@_register
def test_repository_paths_cli_filters_paths_outside_default_scope():
    original_argv = sys.argv
    original_collect = lint.collect_findings
    captured = []

    try:
        lint.collect_findings = lambda paths: captured.extend(paths) or []
        sys.argv = [
            str(LINT_PATH),
            "--repository-paths",
            "docs/design.md",
            "raw/source.md",
            "--report",
            "jsonl",
        ]
        assert lint.main() == 0
    finally:
        lint.collect_findings = original_collect
        sys.argv = original_argv

    assert captured == [REPO_ROOT / "raw" / "source.md"]


@_register
def test_digest_shaped_path_without_manifest_is_not_excluded():
    candidate = (
        REPO_ROOT
        / "raw"
        / "sources"
        / "web"
        / "legacy-page"
        / ("a" * 64)
        / "payload.md"
    )

    assert not lint.is_artifact_bundle_markdown(candidate)


@_register
def test_corrupt_artifact_payload_remains_in_legacy_lint_scope():
    source_payload = min(
        (REPO_ROOT / "raw" / "sources" / "clipping").glob("*/*/payload.md")
    )
    original_root = lint.REPO_ROOT
    with tempfile.TemporaryDirectory() as directory:
        temporary_root = Path(directory)
        relative_bundle = source_payload.parent.relative_to(REPO_ROOT)
        copied_bundle = temporary_root / relative_bundle
        shutil.copytree(source_payload.parent, copied_bundle)
        copied_payload = copied_bundle / source_payload.name
        copied_payload.write_bytes(copied_payload.read_bytes() + b"corrupt")
        lint.REPO_ROOT = temporary_root
        try:
            assert not lint.is_artifact_bundle_markdown(copied_payload)
        finally:
            lint.REPO_ROOT = original_root


@_register
def test_legacy_lint_reports_invalid_utf8_as_high_finding():
    with tempfile.TemporaryDirectory() as directory:
        page = Path(directory) / "invalid-utf8.md"
        page.write_bytes(b"\xff\n")

        findings = lint.collect_legacy_findings([page])

        assert any(
            finding.severity == "HIGH"
            and finding.axis == "io"
            and finding.path == page
            for finding in findings
        )


@_register
def test_legacy_lint_reports_read_error_as_high_finding():
    with tempfile.TemporaryDirectory() as directory:
        page = Path(directory) / "unreadable.md"
        page.write_text("# fixture\n", encoding="utf-8")
        original_read_text = Path.read_text

        def fail_selected(path, *args, **kwargs):
            if path == page:
                raise OSError("injected read failure")
            return original_read_text(path, *args, **kwargs)

        Path.read_text = fail_selected
        try:
            findings = lint.collect_legacy_findings([page])
        finally:
            Path.read_text = original_read_text

        assert any(
            finding.severity == "HIGH"
            and finding.axis == "io"
            and finding.path == page
            and "injected read failure" in finding.message
            for finding in findings
        )


@_register
def test_explicit_missing_path_is_a_high_io_finding():
    with tempfile.TemporaryDirectory(dir=REPO_ROOT) as directory:
        missing = Path(directory) / "missing.md"

        findings = lint.collect_findings([missing])

        assert any(
            finding.severity == "HIGH"
            and finding.axis == "io"
            and finding.path == missing
            for finding in findings
        )


@_register
def test_explicit_symlink_path_is_a_high_io_finding():
    with tempfile.TemporaryDirectory(dir=REPO_ROOT) as directory:
        root = Path(directory)
        target = root / "target.md"
        target.write_text("# fixture\n", encoding="utf-8")
        link = root / "link.md"
        link.symlink_to(target)

        findings = lint.collect_findings([link])

        assert any(
            finding.severity == "HIGH"
            and finding.axis == "io"
            and finding.path == link
            for finding in findings
        )


@_register
def test_explicit_directory_walk_error_is_a_high_io_finding():
    with tempfile.TemporaryDirectory(dir=REPO_ROOT) as directory:
        root = Path(directory)
        original_walk = os.walk

        def fail_walk(path, *args, **kwargs):
            kwargs["onerror"](OSError("injected directory walk failure"))
            return iter(())

        os.walk = fail_walk
        try:
            findings = lint.collect_findings([root])
        finally:
            os.walk = original_walk

        assert any(
            finding.severity == "HIGH"
            and finding.axis == "io"
            and finding.path == root
            and "injected directory walk failure" in finding.message
            for finding in findings
        )


@_register
def test_explicit_external_regular_file_is_a_high_io_finding():
    with tempfile.TemporaryDirectory() as directory:
        external = Path(directory) / "external.md"
        external.write_text("# fixture\n", encoding="utf-8")

        findings = lint.collect_findings([external])

        assert any(
            finding.severity == "HIGH"
            and finding.axis == "io"
            and finding.path == external
            and "outside repository" in finding.message
            for finding in findings
        )


@_register
def test_cli_reports_symlink_input_without_resolving_it():
    with tempfile.TemporaryDirectory(dir=REPO_ROOT) as directory:
        root = Path(directory)
        target = root / "target.md"
        target.write_text("# fixture\n", encoding="utf-8")
        link = root / "link.md"
        link.symlink_to(target)
        original_argv = sys.argv
        try:
            for report in ("text", "jsonl", "markdown"):
                sys.argv = [str(LINT_PATH), "--paths", str(link), "--report", report]
                output = io.StringIO()
                with redirect_stdout(output):
                    exit_code = lint.main()
                assert exit_code == 1
                assert "symbolic links" in output.getvalue()
        finally:
            sys.argv = original_argv


@_register
def test_changed_git_failure_is_a_high_io_finding():
    original_run = lint.subprocess.run
    original_argv = sys.argv

    def fail_git(*args, **kwargs):
        raise lint.subprocess.CalledProcessError(2, args[0], stderr="injected git failure")

    try:
        lint.subprocess.run = fail_git
        sys.argv = [str(LINT_PATH), "--changed", "--report", "jsonl"]
        output = io.StringIO()
        with redirect_stdout(output):
            exit_code = lint.main()
    finally:
        lint.subprocess.run = original_run
        sys.argv = original_argv

    assert exit_code == 1
    assert "Git changed-path inventory failure" in output.getvalue()


@_register
def test_changed_git_os_error_is_a_high_io_finding():
    original_run = lint.subprocess.run
    original_argv = sys.argv

    def fail_git(*args, **kwargs):
        raise OSError("git unavailable")

    try:
        lint.subprocess.run = fail_git
        sys.argv = [str(LINT_PATH), "--changed", "--report", "jsonl"]
        output = io.StringIO()
        with redirect_stdout(output):
            exit_code = lint.main()
    finally:
        lint.subprocess.run = original_run
        sys.argv = original_argv

    assert exit_code == 1
    assert "Git changed-path inventory failure" in output.getvalue()


@_register
def test_changed_git_unicode_error_is_a_high_io_finding():
    original_run = lint.subprocess.run
    original_argv = sys.argv

    def fail_git(*args, **kwargs):
        raise UnicodeError("path decode failure")

    try:
        lint.subprocess.run = fail_git
        sys.argv = [str(LINT_PATH), "--changed", "--report", "jsonl"]
        output = io.StringIO()
        with redirect_stdout(output):
            exit_code = lint.main()
    finally:
        lint.subprocess.run = original_run
        sys.argv = original_argv

    assert exit_code == 1
    assert "Git changed-path inventory failure" in output.getvalue()


@_register
def test_changed_git_non_utf8_path_is_safe_in_every_report_format():
    original_run = lint.subprocess.run
    original_argv = sys.argv

    def non_utf8_path_git(*args, **kwargs):
        return lint.subprocess.CompletedProcess(
            args[0],
            0,
            stdout=b"M\0wiki/bad-\xff.md\0",
        )

    try:
        lint.subprocess.run = non_utf8_path_git
        for report in ("text", "jsonl", "markdown"):
            sys.argv = [str(LINT_PATH), "--changed", "--report", report]
            output = io.StringIO()
            with redirect_stdout(output):
                exit_code = lint.main()
            assert exit_code == 1
            assert "Git changed-path inventory failure" in output.getvalue()
            output.getvalue().encode("utf-8")
    finally:
        lint.subprocess.run = original_run
        sys.argv = original_argv


@_register
def test_changed_git_rejects_non_utf8_non_markdown_record():
    original_run = lint.subprocess.run
    original_argv = sys.argv

    def mixed_path_git(*args, **kwargs):
        return lint.subprocess.CompletedProcess(
            args[0],
            0,
            stdout=b"M\0wiki/ok.md\0M\0wiki/bad-\xff.txt\0",
        )

    try:
        lint.subprocess.run = mixed_path_git
        for report in ("text", "jsonl", "markdown"):
            sys.argv = [str(LINT_PATH), "--changed", "--report", report]
            output = io.StringIO()
            with redirect_stdout(output):
                exit_code = lint.main()
            assert exit_code == 1
            assert "Git changed-path inventory failure" in output.getvalue()
            output.getvalue().encode("utf-8")
    finally:
        lint.subprocess.run = original_run
        sys.argv = original_argv


@_register
def test_changed_git_malformed_status_records_are_high_io_findings():
    original_run = lint.subprocess.run
    original_argv = sys.argv

    try:
        for raw in (
            b"M\0",
            b"R100\0wiki/old.md\0",
            b"M\0../outside.md\0",
            b"M\0\0",
            b"M\0.\0",
            b"M\0./wiki/x.md\0",
            b"M\0wiki//x.md\0",
        ):
            lint.subprocess.run = lambda *args, payload=raw, **kwargs: (
                lint.subprocess.CompletedProcess(args[0], 0, stdout=payload)
            )
            sys.argv = [str(LINT_PATH), "--changed", "--report", "jsonl"]
            output = io.StringIO()
            with redirect_stdout(output):
                exit_code = lint.main()
            assert exit_code == 1
            assert "Git changed-path inventory failure" in output.getvalue()
    finally:
        lint.subprocess.run = original_run
        sys.argv = original_argv


@_register
def test_explicit_non_utf8_path_is_safe_in_every_report_format():
    original_argv = sys.argv
    invalid_path = f"wiki/bad-{chr(0xDCFF)}.md"

    try:
        for report in ("text", "jsonl", "markdown"):
            sys.argv = [str(LINT_PATH), "--paths", invalid_path, "--report", report]
            output = io.StringIO()
            with redirect_stdout(output):
                exit_code = lint.main()
            assert exit_code == 1
            assert "Markdown input path encoding failure" in output.getvalue()
            output.getvalue().encode("utf-8")
    finally:
        sys.argv = original_argv


@_register
def test_changed_paths_are_read_from_repository_root_with_nul_delimiters():
    original_run = lint.subprocess.run
    calls = []

    def capture_git(*args, **kwargs):
        calls.append((args, kwargs))
        return lint.subprocess.CompletedProcess(args[0], 0, stdout=b"M\0AGENTS.md\0")

    lint.subprocess.run = capture_git
    try:
        paths = lint.git_changed_paths("HEAD^")
    finally:
        lint.subprocess.run = original_run

    assert paths == [REPO_ROOT / "AGENTS.md"]
    assert len(calls) == 1
    args, kwargs = calls[0]
    assert args[0] == [
        "git",
        "diff",
        "--no-renames",
        "--name-status",
        "-z",
        "HEAD^..HEAD",
    ]
    assert kwargs["cwd"] == REPO_ROOT
    assert kwargs["text"] is False


def _changed_paths_for_markdown_transition(
    destination: str | None,
    canonical_findings: tuple[dict, ...] = (),
) -> tuple[Path, list[Path], int, str, list[tuple]]:
    original_root = lint.REPO_ROOT
    original_wiki = lint.WIKI_DIR
    original_target = lint.check_target
    original_drift = lint.generated_drift
    original_argv = sys.argv
    target_calls = []
    with tempfile.TemporaryDirectory() as directory:
        repo = Path(directory).resolve()
        commands = (
            ["git", "init", "-q"],
            ["git", "config", "user.name", "test"],
            ["git", "config", "user.email", "test@example.invalid"],
        )
        for command in commands:
            lint.subprocess.run(command, cwd=repo, check=True)
        wiki = repo / "wiki"
        wiki.mkdir()
        source = wiki / "old.md"
        source.write_text("# old\n", encoding="utf-8")
        lint.subprocess.run(["git", "add", "wiki/old.md"], cwd=repo, check=True)
        lint.subprocess.run(["git", "commit", "-qm", "base"], cwd=repo, check=True)
        if destination is None:
            source.unlink()
        else:
            source.rename(wiki / destination)
        lint.subprocess.run(["git", "add", "-A"], cwd=repo, check=True)
        lint.subprocess.run(["git", "commit", "-qm", "transition"], cwd=repo, check=True)

        class Result:
            findings = canonical_findings

        def target(*args, **kwargs):
            target_calls.append((args, kwargs))
            return Result()

        lint.REPO_ROOT = repo
        lint.WIKI_DIR = wiki
        lint.check_target = target
        lint.generated_drift = lambda *args, **kwargs: ()
        try:
            paths = lint.git_changed_paths("HEAD^")
            sys.argv = [str(LINT_PATH), "--changed", "--base", "HEAD^", "--report", "jsonl"]
            output = io.StringIO()
            with redirect_stdout(output):
                exit_code = lint.main()
        finally:
            lint.REPO_ROOT = original_root
            lint.WIKI_DIR = original_wiki
            lint.check_target = original_target
            lint.generated_drift = original_drift
            sys.argv = original_argv
        return repo, paths, exit_code, output.getvalue(), target_calls


@_register
def test_changed_paths_preserve_markdown_source_renamed_to_non_markdown():
    repo, paths, exit_code, output, target_calls = _changed_paths_for_markdown_transition(
        "renamed.txt"
    )
    assert paths == [repo / "wiki"]
    assert exit_code == 0
    assert "Markdown inventory stat failure" not in output
    assert len(target_calls) == 1


@_register
def test_changed_paths_preserve_deleted_markdown_source():
    repo, paths, exit_code, _, target_calls = _changed_paths_for_markdown_transition(None)
    assert paths == [repo / "wiki"]
    assert exit_code == 0
    assert len(target_calls) == 1


@_register
def test_changed_paths_preserve_both_markdown_rename_paths():
    repo, paths, exit_code, _, target_calls = _changed_paths_for_markdown_transition(
        "renamed.md"
    )
    assert paths == [repo / "wiki"]
    assert exit_code == 0
    assert len(target_calls) == 1


@_register
def test_changed_delete_propagates_canonical_broken_link_finding():
    finding = {
        "severity": "HIGH",
        "rule_id": "VR-KP-008",
        "path": "wiki/domains/test/ref.md",
        "line": 1,
        "message": "broken link: wiki/old.md",
    }
    _, _, exit_code, output, target_calls = _changed_paths_for_markdown_transition(
        None, (finding,)
    )
    assert exit_code == 1
    assert "broken link: wiki/old.md" in output
    assert len(target_calls) == 1


def _changed_non_wiki_delete(replacement: bytes | str | None) -> tuple[int, str]:
    original_root = lint.REPO_ROOT
    original_argv = sys.argv
    with tempfile.TemporaryDirectory() as directory:
        repo = Path(directory).resolve()
        for command in (
            ["git", "init", "-q"],
            ["git", "config", "user.name", "test"],
            ["git", "config", "user.email", "test@example.invalid"],
        ):
            lint.subprocess.run(command, cwd=repo, check=True)
        docs = repo / "docs"
        docs.mkdir()
        deleted = docs / "x.md"
        deleted.write_text("# base\n", encoding="utf-8")
        lint.subprocess.run(["git", "add", "docs/x.md"], cwd=repo, check=True)
        lint.subprocess.run(["git", "commit", "-qm", "base"], cwd=repo, check=True)
        deleted.unlink()
        lint.subprocess.run(["git", "add", "-A"], cwd=repo, check=True)
        lint.subprocess.run(["git", "commit", "-qm", "delete"], cwd=repo, check=True)
        if isinstance(replacement, bytes):
            deleted.write_bytes(replacement)
        elif replacement == "symlink":
            target = docs / "target.md"
            target.write_text("# target\n", encoding="utf-8")
            deleted.symlink_to(target)

        lint.REPO_ROOT = repo
        try:
            sys.argv = [str(LINT_PATH), "--changed", "--base", "HEAD^", "--report", "jsonl"]
            output = io.StringIO()
            with redirect_stdout(output):
                exit_code = lint.main()
        finally:
            lint.REPO_ROOT = original_root
            sys.argv = original_argv
        return exit_code, output.getvalue()


@_register
def test_changed_non_wiki_clean_delete_does_not_read_missing_leaf():
    exit_code, output = _changed_non_wiki_delete(None)
    assert exit_code == 0
    assert output == ""


@_register
def test_changed_non_wiki_delete_recreated_with_invalid_utf8_fails():
    exit_code, output = _changed_non_wiki_delete(b"\xff")
    assert exit_code == 1
    assert "Markdown read failure" in output


@_register
def test_changed_non_wiki_delete_recreated_as_symlink_fails():
    exit_code, output = _changed_non_wiki_delete("symlink")
    assert exit_code == 1
    assert "rejects symbolic links" in output


@_register
def test_changed_paths_preserve_newline_in_markdown_filename():
    original_run = lint.subprocess.run

    def newline_path_git(*args, **kwargs):
        return lint.subprocess.CompletedProcess(
            args[0],
            0,
            stdout=b"M\0docs/line\nbreak.md\0M\0docs/ignored.txt\0",
        )

    lint.subprocess.run = newline_path_git
    try:
        paths = lint.git_changed_paths("HEAD^")
    finally:
        lint.subprocess.run = original_run

    assert paths == [REPO_ROOT / "docs" / "line\nbreak.md"]


@_register
def test_human_reports_escape_newline_and_backtick_paths():
    original_argv = sys.argv
    unusual_path = REPO_ROOT / "docs" / "line\nbreak`x.md"

    try:
        for report in ("text", "markdown"):
            sys.argv = [str(LINT_PATH), "--paths", str(unusual_path), "--report", report]
            output = io.StringIO()
            with redirect_stdout(output):
                exit_code = lint.main()
            rendered = output.getvalue()
            assert exit_code == 1
            assert "line\nbreak" not in rendered
            assert "line\\nbreak" in rendered
            if report == "markdown":
                assert "\\`x.md" in rendered
    finally:
        sys.argv = original_argv


@_register
def test_default_missing_wiki_root_is_a_high_io_finding():
    original_wiki = lint.WIKI_DIR
    original_argv = sys.argv
    with tempfile.TemporaryDirectory(dir=REPO_ROOT) as directory:
        lint.WIKI_DIR = Path(directory) / "missing-wiki"
        try:
            sys.argv = [str(LINT_PATH), "--report", "jsonl"]
            output = io.StringIO()
            with redirect_stdout(output):
                exit_code = lint.main()
        finally:
            lint.WIKI_DIR = original_wiki
            sys.argv = original_argv

    assert exit_code == 1
    assert "Markdown inventory stat failure" in output.getvalue()


@_register
def test_collect_findings_inventories_each_input_once():
    original_inventory = lint._markdown_inventory
    calls = 0

    def counting_inventory(paths):
        nonlocal calls
        calls += 1
        return original_inventory(paths)

    lint._markdown_inventory = counting_inventory
    try:
        lint.collect_findings([REPO_ROOT / "AGENTS.md"])
    finally:
        lint._markdown_inventory = original_inventory

    assert calls == 1


@_register
def test_canonical_wiki_dispatch_never_falls_back_to_legacy_checks():
    original_target = lint.check_target
    original_legacy = lint.collect_legacy_findings
    calls = []

    class Result:
        findings = (
            {
                "severity": "HIGH",
                "rule_id": "VR-KP-004",
                "path": str(lint.WIKI_DIR / "broken.md"),
                "line": 1,
                "message": "invalid canonical page",
            },
        )

    try:
        def target(*args, **kwargs):
            calls.append("canonical")
            return Result()

        def legacy(paths):
            calls.append("legacy")
            return []

        lint.check_target = target
        lint.collect_legacy_findings = legacy
        findings = lint.collect_findings([lint.WIKI_DIR])
        assert calls == ["canonical"]
        assert len(findings) == 1
        assert findings[0].message == "invalid canonical page"
    finally:
        lint.check_target = original_target
        lint.collect_legacy_findings = original_legacy


@_register
def test_wiki_dispatch_includes_generated_repository_drift():
    original_target = lint.check_target
    missing = object()
    original_drift = getattr(lint, "generated_drift", missing)
    original_surface = getattr(lint, "generated_surface_findings", missing)

    class Result:
        findings = ()

    try:
        lint.check_target = lambda *args, **kwargs: Result()
        lint.generated_drift = lambda *args, **kwargs: (
            "generated bytes differ: wiki/templates/concept.md",
        )
        lint.generated_surface_findings = lambda drift: [
            {
                "severity": "HIGH",
                "rule_id": "VR-KP-017",
                "path": "wiki/templates/concept.md",
                "message": drift[0],
            }
        ]

        findings = lint.collect_findings([lint.WIKI_DIR])

        assert len(findings) == 1
        assert findings[0].axis == "VR-KP-017"
        assert "generated bytes differ" in findings[0].message
    finally:
        lint.check_target = original_target
        if original_drift is missing:
            del lint.generated_drift
        else:
            lint.generated_drift = original_drift
        if original_surface is missing:
            del lint.generated_surface_findings
        else:
            lint.generated_surface_findings = original_surface


@_register
def test_legacy_wiki_validator_surface_is_removed():
    for name in (
        "WIKI_REQUIRED_FIELDS",
        "CLAIM_TABLE_COLUMNS",
        "check_axis_1_accuracy",
        "check_wiki_required_fields",
        "check_claim_table",
        "parse_claim_table",
        "calculate_claim_rollup",
    ):
        assert not hasattr(lint, name), name


@_register
def test_raw_last_verified_is_not_exempted_by_evergreen():
    path = REPO_ROOT / "raw" / "sources" / "web" / "fixture.md"

    missing = lint.check_axis_6_recency(path, {"evergreen": True})
    old = lint.check_axis_6_recency(
        path,
        {"page_type": "concept", "evergreen": True, "last_verified": "2000-01-01"},
    )

    assert any(
        finding.severity == "HIGH" and "누락" in finding.message
        for finding in missing
    )
    assert any(
        finding.severity == "HIGH" and "≥730" in finding.message
        for finding in old
    )
    assert all("면제" not in finding.message for finding in old)


@_register
def test_authored_path_containing_raw_sources_segments_is_not_raw():
    path = REPO_ROOT / "development" / "raw" / "sources" / "fixture.md"

    findings = lint.check_axis_6_recency(
        path,
        {"page_type": "concept", "evergreen": True, "last_verified": "2000-01-01"},
    )

    assert not any(finding.severity == "HIGH" for finding in findings)
    assert any(finding.severity == "MEDIUM" for finding in findings)


@_register
def test_non_authored_concept_does_not_receive_evergreen_exemption():
    path = REPO_ROOT / "projects" / "fixture.md"

    findings = lint.check_axis_6_recency(
        path,
        {"page_type": "concept", "evergreen": True, "last_verified": "2000-01-01"},
    )

    assert any(finding.severity == "HIGH" for finding in findings)
    assert all("면제" not in finding.message for finding in findings)


@_register
def test_concept_evergreen_only_exempts_recency_hard_fail():
    path = REPO_ROOT / "development" / "fixture.md"

    findings = lint.check_axis_6_recency(
        path,
        {"page_type": "concept", "evergreen": True, "last_verified": "2000-01-01"},
    )

    assert not any(finding.severity == "HIGH" for finding in findings)
    assert any(
        finding.severity == "MEDIUM" and "≥180" in finding.message
        for finding in findings
    )


def main() -> int:
    passed = 0
    failed = 0
    for fn in TESTS:
        try:
            fn()
            print(f"PASS {fn.__name__}")
            passed += 1
        except Exception as exc:
            print(f"FAIL {fn.__name__}: {exc}")
            failed += 1
    print(f"\n--- {passed} passed, {failed} failed / {len(TESTS)} ---")
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
