"""
ui 包

命令行交互界面
"""

from .cli import CLI, EnhancedCLI, get_cli
from .widgets import (
    Colors, Icons, print_header, print_panel, print_progress_bar,
    print_table, print_card, print_status, print_section_header,
    print_workflow_status, print_checkpoint_prompt, print_welcome
)
from .display import (
    display_paper_list, display_gap_report, display_method_design,
    display_experiment_plan, display_paper_draft, display_review_report,
    display_project_status, display_help
)
from .interactive import ConfirmationHandler

__all__ = [
    # CLI
    "CLI",
    "EnhancedCLI",
    "get_cli",
    # Widgets
    "Colors",
    "Icons",
    "print_header",
    "print_panel",
    "print_progress_bar",
    "print_table",
    "print_card",
    "print_status",
    "print_section_header",
    "print_workflow_status",
    "print_checkpoint_prompt",
    "print_welcome",
    # Display
    "display_paper_list",
    "display_gap_report",
    "display_method_design",
    "display_experiment_plan",
    "display_paper_draft",
    "display_review_report",
    "display_project_status",
    "display_help",
    # Interactive
    "ConfirmationHandler",
]
