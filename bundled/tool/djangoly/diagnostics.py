import json
from lsprotocol.types import Diagnostic, DiagnosticSeverity, Position, Range

from .run_check import run_djangoly_on_file


def get_diagnostics(file_path):
    output = run_djangoly_on_file(file_path)
    diagnostics = []
    for issue in parse_djangoly_output(output):
        diagnostic = Diagnostic(
            range=Range(
                start=Position(issue['line'], issue['col']),
                end=Position(issue['line'], issue['end_col'])
            ),
            message=issue['message'],
            severity=DiagnosticSeverity.Error if issue['severity'] == 'high' else DiagnosticSeverity.Warning,
        )
        diagnostics.append(diagnostic)
    return diagnostics



def parse_djangoly_output(djangoly_output: str) -> list[Diagnostic]:
    """
    Parse the JSON output from Djangoly and return a list of diagnostics.
    """
    try:
        # Assume Djangoly returns a JSON string
        issues = json.loads(djangoly_output)
        diagnostics = []

        for issue in issues:
            # Map severity from Djangoly to LSP DiagnosticSeverity
            severity = DiagnosticSeverity.Error if issue.get('severity') == 'high' else DiagnosticSeverity.Warning

            # Create a diagnostic for each issue
            diagnostic = Diagnostic(
                range=Range(
                    start=Position(line=issue['line'] - 1, character=issue['col']),
                    end=Position(line=issue['line'] - 1, character=issue['end_col'])
                ),
                message=issue['message'],
                severity=severity,
            )
            diagnostics.append(diagnostic)

        return diagnostics

    except json.JSONDecodeError as e:
        print(f"Error decoding Djangoly output: {str(e)}")
        return []

