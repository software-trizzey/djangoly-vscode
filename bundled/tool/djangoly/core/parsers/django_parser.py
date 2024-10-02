import ast
import json
from typing import Optional, Dict, Any
from ..utils.log import LOGGER
from ..utils.constants import DJANGO_IGNORE_FUNCTIONS
from .ast_parser import Analyzer
from ..checks.security.checker import SecurityCheckService
from ..checks.model_fields import ModelFieldCheckService
from ..checks.skinny_views.checker import ViewComplexityAnalyzer
from ..checks.skinny_views.scorer import ViewComplexityScorer, ScoreThresholds
from ..checks.exception_handlers.checker import ExceptionHandlingCheckService
from ..checks.redundant_queryset_methods.checker import RedundantQueryMethodCheckService
from ..utils.issue import IssueSeverity
from ..services.view_detector import DjangoViewDetectionService, DjangoViewType
from ..services.function_node import FunctionNodeService

class DjangoAnalyzer(Analyzer):
    def __init__(
        self,
        file_path: str,
        source_code,
        conventions: Dict[str, Any],
        settings: Dict[str, Any],
        model_cache_json: str
    ):
        super().__init__(file_path, source_code, conventions, settings)
        self.current_django_class_type = None
        self.model_cache = self.parse_model_cache(model_cache_json)
        self.class_type_cache = {}
        self.class_definitions = {}
        self.security_service = SecurityCheckService(source_code)
        self.security_issues = []
        self.model_field_check_service = ModelFieldCheckService(source_code)
        LOGGER.debug(f"Model cache: {self.model_cache}")
        self.view_detection_service = DjangoViewDetectionService()
        self.complexity_scorer = ViewComplexityScorer(ScoreThresholds(line_threshold=100, operation_threshold=25))
        self.complexity_analyzer = ViewComplexityAnalyzer(source_code, self.complexity_scorer)
        self.exception_handler_service = ExceptionHandlingCheckService(source_code)
        self.function_node_service = FunctionNodeService()
        self.redundant_queryset_check_service = RedundantQueryMethodCheckService(source_code)

    def parse_model_cache(self, model_cache_json):
        try:
            return json.loads(model_cache_json)
        except json.JSONDecodeError as e:
            LOGGER.error(f"Error parsing model cache JSON: {e}")
            return {}

    def get_model_info(self, model_name: str) -> Optional[dict]:
        model_info = self.model_cache.get(model_name)
        if model_info:
            LOGGER.debug(f"Found model info for {model_name}: {model_info}")
            return model_info
        else:
            LOGGER.debug(f"Model info for {model_name} not found in cache")
            return None

    def get_class_definitions(self):
        LOGGER.debug("Collecting Django class definitions...")
        for node in ast.walk(self.tree):
            if isinstance(node, ast.ClassDef):
                self.class_definitions[node.name] = node
        LOGGER.debug(f"Collected {len(self.class_definitions)} class definitions.")

    def check_function_node_for_issues(self, node, symbol_type, body, body_with_lines, function_start_line, function_end_line, function_start_col, function_end_col, decorators, calls, arguments, is_reserved):
        message, severity, issue_code = None, None, None

        if symbol_type == DjangoViewType.FUNCTIONAL_VIEW or symbol_type == f'{DjangoViewType.CLASS_VIEW}_method':
            try:
                complexity_issue = self.complexity_analyzer.run_complexity_analysis(node)
                if complexity_issue:
                    issue_code = complexity_issue.code
                    message = complexity_issue.message
                    severity = complexity_issue.severity
            except RecursionError:
                LOGGER.error(f"Caught Recursion error while running complexity analysis on {node.name}")
                message = "Encountered error during complexity analysis"
                severity = IssueSeverity.INFORMATION

            exception_handling_issue = self.exception_handler_service.run_check(node)
            if exception_handling_issue:
                full_line_text = self.source_code.splitlines()[node.lineno - 1]
                full_line_length = len(full_line_text)
                self.add_diagnostic(
                    type=symbol_type,
                    name=node.name,
                    issue_code=exception_handling_issue.code,
                    message=exception_handling_issue.message,
                    severity=exception_handling_issue.severity,
                    line=node.lineno,
                    col_offset=node.col_offset,
                    end_col_offset=node.col_offset + len(node.name),
                    is_reserved=False,
                    body=body,
                    body_with_lines=body_with_lines,
                    function_start_line=function_start_line,
                    function_end_line=function_end_line,
                    function_start_col=function_start_col,
                    function_end_col=function_end_col,
                    decorators=decorators,
                    calls=calls,
                    arguments=arguments,
                    full_line_length=full_line_length
                )

        return message, severity, issue_code

    def visit_ClassDef(self, node):
        security_issues = self.security_service.check_raw_sql(node)
        if security_issues:
            for issue in security_issues:
                self.add_diagnostic(
                    type='security', # TODO: is this the right type?
                    name=node.name,
                    line=issue.lineno,
                    col_offset=issue.col_offset,
                    end_col_offset=issue.end_col_offset,
                    severity=issue.severity,
                    message=issue.message,
                    issue_code=issue.code
                )

        self.in_class = True
        class_type = self.view_detection_service.get_django_class_type(node, self.class_definitions)

        if class_type == DjangoViewType.CLASS_VIEW:
            issue = self.complexity_analyzer.run_complexity_analysis(node)
            LOGGER.debug(f"Ran complexity analysis on {node.name}")
            
            if issue:
                LOGGER.debug(f'Complexity issue detected for view class {node.name}: {issue}')
                comments = self.get_related_comments(node)
                self.add_diagnostic(
                    type=DjangoViewType.CLASS_VIEW,
                    name=node.name,
                    message=issue.message,
                    severity=issue.severity,
                    issue_code=issue.code,
                    comments=comments,
                    line=node.lineno,
                    col_offset=node.col_offset,
                    end_col_offset=node.col_offset + len(node.name),
                    is_reserved=False
                )
            self.current_django_class_type = DjangoViewType.CLASS_VIEW
        else:
            self.current_django_class_type = None

        self.generic_visit(node)
        self.in_class = False
        self.current_django_class_type = None

    def visit_FunctionDef(self, node):
        comments = self.get_related_comments(node)
        is_reserved = DJANGO_IGNORE_FUNCTIONS.get(node.name, False) or self.is_python_reserved(node.name)
        function_start_line, function_start_col = node.lineno, node.col_offset

        function_end_line, function_end_col = self.function_node_service.get_function_end_position(node, self.source_code)
        if not node.body:
            function_end_line, function_end_col = self.function_node_service.get_empty_function_position(function_start_line, function_start_col, node.name)

        body_with_lines, body = self.get_function_body(node)
        decorators = [ast.get_source_segment(self.source_code, decorator) for decorator in node.decorator_list]
        calls = []
        arguments = self.extract_arguments(node.args)

        redundant_query_issue = self.redundant_queryset_check_service.run_check(node)
        if redundant_query_issue:
            self.add_diagnostic(
                type=redundant_query_issue.code,
                severity=redundant_query_issue.severity,
                message=redundant_query_issue.message,
                line=redundant_query_issue.lineno,
                method_chain=redundant_query_issue.method_chain,
                simplified_chain=redundant_query_issue.simplified_chain,
                col_offset=redundant_query_issue.col_offset,
                end_col_offset=redundant_query_issue.end_col_offset
            )
            return

        symbol_type = self.function_node_service.get_symbol_type(node, self.in_class, self.current_django_class_type, self.view_detection_service)

        message, severity, issue_code = self.check_function_node_for_issues(
            node,
            symbol_type,
            body,
            body_with_lines,
            function_start_line,
            function_end_line,
            function_start_col,
            function_end_col,
            decorators,
            calls,
            arguments,
            is_reserved
        )

        if not message and not issue_code:
            return

        self.add_diagnostic(
            type=symbol_type,
            name=node.name,
            message=message,
            severity=severity,
            issue_code=issue_code,
            comments=comments,
            line=function_start_line,
            col_offset=function_start_col,
            end_col_offset=function_end_col,
            is_reserved=is_reserved,
            body=body,
            body_with_lines=body_with_lines,
            function_start_line=function_start_line,
            function_end_line=function_end_line,
            function_start_col=function_start_col,
            function_end_col=function_end_col,
            decorators=decorators,
            calls=calls,
            arguments=arguments
        )

        self.generic_visit(node)

    def visit_Assign(self, node):
        for target in node.targets:
            if isinstance(target, ast.Name):
                security_issues = self.security_service.check_assignment_security(
                    target.id, node.value, node.lineno
                )
                if security_issues:
                    for issue in security_issues:
                        self.add_diagnostic(
                            type='assignment',
                            name=target.id,
                            line=node.lineno,
                            col_offset=node.col_offset,
                            end_col_offset=node.col_offset + len(target.id),
                            severity=issue.severity,
                            message=issue.message,
                            issue_code=issue.code
                        )

                value_source = ast.get_source_segment(self.source_code, node.value)
                comments = self.get_related_comments(node)

                field_issues = self.model_field_check_service.run_model_field_checks(node)

                if self.in_class and self.current_django_class_type:
                    symbol_type = f'{self.current_django_class_type}_field'
                else:
                    symbol_type = 'django_model_field' # Was 'assignment' type. See if this breaks
                
                for issue in field_issues:
                    self.add_diagnostic(
                        type=symbol_type,
                        name=target.id,
                        comments=comments,
                        line=node.lineno,
                        col_offset=node.col_offset,
                        end_col_offset=node.col_offset + len(target.id),
                        is_reserved=False,
                        value=value_source,
                        severity=issue.severity,
                        message=issue.message,
                        issue_code=issue.code,
                        related_issues=[issue]
                    )

        self.generic_visit(node)

    def parse_code(self):
        try:
            LOGGER.debug("Parsing Django code")
            self.get_comments()
            self.tree = ast.parse(self.source_code)
            self.get_class_definitions()

            super().visit(self.tree)
            self.view_detection_service.initialize(self.tree)

            return {
                "diagnostics": self.diagnostics,
                "diagnostics_count": len(self.diagnostics)
            }
        except SyntaxError as e:
            LOGGER.warning(f"Syntax error detected while parsing Django code: {e}")
            return {
                "diagnostics": self.diagnostics,
                "diagnostics_count": len(self.diagnostics),
                "error": "Syntax error detected",
                "details": str(e)
            }
        except Exception as e:
            LOGGER.error(f'Error parsing Django code: {e}')
            return {
                "diagnostics": self.diagnostics,
                "diagnostics_count": len(self.diagnostics),
                "error": "General error detected",
                "details": str(e)
            }
