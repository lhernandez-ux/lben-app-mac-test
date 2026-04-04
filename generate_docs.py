import os

def generate_code_md():
    root_dir = os.getcwd()
    output_file = os.path.join(root_dir, 'codigoproyecto.md')
    
    ignore_dirs = {'.git', '.venv', '__pycache__', '.mypy_cache', 'assets', 'data', 'docs', 'tests'}
    ignore_files = {'arbolproyecto.md', 'codigoproyecto.md', 'tmp_inspect_excel.py', 'generate_docs.py'}
    
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write("# Código Completo del Proyecto\n\n")
        
        for root, dirs, files in os.walk(root_dir):
            dirs[:] = [d for d in dirs if d not in ignore_dirs]
            files.sort()
            
            if not files:
                continue
                
            rel_path = os.path.relpath(root, root_dir)
            if rel_path == '.':
                header = "Raíz del Proyecto"
            else:
                header = rel_path.replace(os.sep, ' / ').title()
                
            f.write(f"## {header}\n\n")
            
            for file in files:
                if file in ignore_files or file.endswith(('.xlsx', '.pdf', '.png', '.jpg', '.ico')):
                    continue
                
                file_path = os.path.join(root, file)
                f.write(f"### {file}\n\n")
                f.write("```python\n")
                try:
                    with open(file_path, 'r', encoding='utf-8') as code_file:
                        f.write(code_file.read())
                except Exception as e:
                    f.write(f"# Error leyendo archivo: {e}\n")
                f.write("\n```\n\n")

def generate_tree(root_dir, ignore_dirs, ignore_files):
    tree_file = os.path.join(root_dir, 'arbolproyecto.md')
    with open(tree_file, 'w', encoding='utf-8') as f:
        f.write("# Estructura del Proyecto\n\n```text\n")
        f.write("LBEn_APP_Resol016/\n")
        
        for root, dirs, files in os.walk(root_dir):
            dirs[:] = [d for d in dirs if d not in ignore_dirs]
            rel_root = os.path.relpath(root, root_dir)
            if rel_root == '.':
                level = 0
            else:
                level = rel_root.count(os.sep) + 1
            
            if level > 0:
                indent = '│   ' * (level - 1) + '├── '
                f.write(f"{indent}{os.path.basename(root)}/\n")
            
            sub_indent = '│   ' * level + '├── '
            for file in sorted(files):
                if file in ignore_files or file.startswith('.') or file.endswith('.pyc'):
                    continue
                f.write(f"{sub_indent}{file}\n")
        f.write("```\n")

if __name__ == "__main__":
    generate_code_md()
    ignore_dirs_tree = {'.git', '.venv', '__pycache__', '.mypy_cache'}
    ignore_files_tree = {'arbolproyecto.md', 'codigoproyecto.md', 'generate_docs.py', 'tmp_inspect_excel.py'}
    generate_tree(os.getcwd(), ignore_dirs_tree, ignore_files_tree)
