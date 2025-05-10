from typing import Dict, List

# Define code file extensions to include
CODE_EXTENSIONS: List[str] = [
    # Python
    ".py",
    ".pyx",
    ".pyi",
    # JavaScript/TypeScript
    ".js",
    ".jsx",
    ".ts",
    ".tsx",
    # Java
    ".java",
    ".kt",
    ".scala",
    # C/C++/C#
    ".c",
    ".cpp",
    ".h",
    ".hpp",
    ".cs",
    # Ruby
    ".rb",
    # PHP
    ".php",
    # Go
    ".go",
    # Rust
    ".rs",
    # Swift
    ".swift",
    # Shell
    ".sh",
    ".bash",
    # HTML/CSS
    ".html",
    ".htm",
    ".css",
    ".scss",
    ".sass",
    ".less",
    # Other
    ".json",
    ".yaml",
    ".yml",
    ".xml",
    ".md",
    ".sql",
]

# Map file extensions to language names for text splitter
LANGUAGE_MAP: Dict[str, str] = {
    # Python
    ".py": "python",
    ".pyx": "python",
    ".pyi": "python",
    # JavaScript/TypeScript
    ".js": "js",
    ".jsx": "js",
    ".ts": "ts",  # changed from "typescript" to "ts"
    ".tsx": "ts",  # changed from "typescript" to "ts"
    # Java and JVM languages
    ".java": "java",
    ".kt": "kotlin",  # changed from "java" to "kotlin"
    ".scala": "scala",
    # C/C++/C#
    ".c": "c",  # changed from "cpp" to "c"
    ".cpp": "cpp",
    ".h": "cpp",
    ".hpp": "cpp",
    ".cs": "csharp",
    # Ruby
    ".rb": "ruby",
    # PHP
    ".php": "php",
    # Go
    ".go": "go",
    # Rust
    ".rs": "rust",
    # Swift
    ".swift": "swift",
    # Shell - no direct match, keeping as is
    ".sh": "text",
    ".bash": "text",
    # HTML/CSS
    ".html": "html",
    ".htm": "html",
    ".css": "text",  # CSS doesn't have specific splitter
    ".scss": "text",
    ".sass": "text",
    ".less": "text",
    # Others - keeping non-matching types as is
    ".json": "json",
    ".yaml": "text",
    ".yml": "text",
    ".xml": "text",
    ".md": "markdown",
    ".sql": "text",
    # Additional languages from the enum
    ".proto": "proto",
    ".rst": "rst",
    ".sol": "sol",
    ".cbl": "cobol",
    ".cob": "cobol",
    ".lua": "lua",
    ".pl": "perl",
    ".pm": "perl",
    ".hs": "haskell",
    ".ex": "elixir",
    ".exs": "elixir",
    ".ps1": "powershell",
    ".tex": "latex",
}
