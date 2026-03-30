
import curses
import subprocess
import os

class GitTUI:
    def __init__(self, stdscr):
        self.stdscr = stdscr
        curses.curs_set(0)  # Hide cursor
        self.stdscr.nodelay(1) # Non-blocking input
        self.stdscr.timeout(100) # Refresh every 100ms

        self.panels = {
            "status": [],
            "commits": [],
            "diff": []
        }
        self.active_panel = "status"
        self.selected_lines = {
            "status": 0,
            "commits": 0,
            "diff": 0
        }
        self.is_git_repo = False
        self.repo_path = os.getcwd()
        self.check_git_repo()
        self.update_data()

    def check_git_repo(self):
        try:
            subprocess.run(["git", "rev-parse", "--is-inside-work-tree"], cwd=self.repo_path, capture_output=True, check=True)
            self.is_git_repo = True
        except subprocess.CalledProcessError:
            self.is_git_repo = False

    def run_git_command(self, command):
        try:
            result = subprocess.run(command, cwd=self.repo_path, capture_output=True, text=True, check=True)
            return result.stdout.splitlines()
        except subprocess.CalledProcessError as e:
            return [f"Erro: {e.stderr.strip()}"]
        except FileNotFoundError:
            return ["Erro: Git não encontrado. Certifique-se de que está instalado e no PATH."]

    def update_data(self):
        if not self.is_git_repo:
            self.panels["status"] = ["Não é um repositório Git.", "Pressione 'i' para inicializar um novo repositório Git aqui."]
            self.panels["commits"] = ["Não é um repositório Git."]
            self.panels["diff"] = ["Não é um repositório Git."]
            return

        # Update status
        self.panels["status"] = self.run_git_command(["git", "status", "--porcelain"])
        if not self.panels["status"] or (len(self.panels["status"]) == 1 and self.panels["status"][0].startswith("Erro:")):
            self.panels["status"] = ["Nenhuma alteração pendente."]

        # Update commits
        self.panels["commits"] = self.run_git_command(["git", "log", "--oneline", "-n", "20"])
        if not self.panels["commits"] or (len(self.panels["commits"]) == 1 and self.panels["commits"][0].startswith("Erro:")):
            self.panels["commits"] = ["Nenhum commit encontrado."]

        # Update diff for selected status file
        selected_file = self.get_selected_file_from_status()
        if selected_file:
            self.panels["diff"] = self.run_git_command(["git", "diff", selected_file])
        else:
            self.panels["diff"] = ["Selecione um arquivo no painel de status para ver o diff."]

    def get_selected_file_from_status(self):
        if self.active_panel == "status" and self.panels["status"] and self.is_git_repo:
            line = self.panels["status"][self.selected_lines["status"]]
            if not line.startswith("Nenhuma alteração") and not line.startswith("Não é um repositório"):
                parts = line.strip().split(maxsplit=1)
                if len(parts) > 1:
                    return parts[1]
        return None

    def draw_panel(self, window, title, content, is_active, selected_line_idx):
        window.clear()
        h, w = window.getmaxyx()
        window.box()
        window.addstr(0, 2, f" {title} ", curses.A_REVERSE if is_active else curses.A_NORMAL)

        for i, line in enumerate(content):
            if i >= h - 2: # Leave space for border
                break
            display_line = line[:w-4] # Truncate to fit window width
            attr = curses.A_NORMAL
            if i == selected_line_idx and is_active:
                attr = curses.A_REVERSE
            window.addstr(i + 1, 2, display_line, attr)
        window.refresh()

    def draw_ui(self):
        h, w = self.stdscr.getmaxyx()

        # Define panel sizes and positions
        status_h = h // 2
        status_w = w // 2
        commits_h = h // 2
        commits_w = w - status_w
        diff_h = h - status_h
        diff_w = w

        self.status_window = curses.newwin(status_h, status_w, 0, 0)
        self.commits_window = curses.newwin(commits_h, commits_w, 0, status_w)
        self.diff_window = curses.newwin(diff_h, diff_w, status_h, 0)

        self.draw_panel(self.status_window, "Status", self.panels["status"], self.active_panel == "status", self.selected_lines["status"])
        self.draw_panel(self.commits_window, "Commits", self.panels["commits"], self.active_panel == "commits", self.selected_lines["commits"])
        self.draw_panel(self.diff_window, "Diff", self.panels["diff"], self.active_panel == "diff", self.selected_lines["diff"])

        self.stdscr.refresh()

    def handle_input(self, c):
        current_panel_content = self.panels[self.active_panel]
        current_selection_idx = self.selected_lines[self.active_panel]

        if c == curses.KEY_UP:
            if current_selection_idx > 0:
                self.selected_lines[self.active_panel] -= 1
        elif c == curses.KEY_DOWN:
            if current_selection_idx < len(current_panel_content) - 1:
                self.selected_lines[self.active_panel] += 1
        elif c == ord("\t"): # Tab to switch panels
            if self.active_panel == "status":
                self.active_panel = "commits"
            elif self.active_panel == "commits":
                self.active_panel = "diff"
            else:
                self.active_panel = "status"
        elif c == ord("q"):
            return False # Quit
        elif not self.is_git_repo and c == ord("i"): # Initialize git repo
            self.run_git_command(["git", "init"])
            self.check_git_repo()
            self.update_data()
        elif self.is_git_repo:
            if self.active_panel == "status" and c == ord("a"): # Add file to staging
                selected_file = self.get_selected_file_from_status()
                if selected_file:
                    self.run_git_command(["git", "add", selected_file])
                    self.update_data()
            elif self.active_panel == "status" and c == ord("c"): # Commit changes
                # This is a simplified commit. In a real TUI, it would open an editor.
                # For now, we'll just do a dummy commit.
                self.run_git_command(["git", "commit", "-m", "Dummy commit from TUI"]) # Simplified
                self.update_data()

        return True

    def main_loop(self):
        running = True
        while running:
            self.update_data()
            self.draw_ui()
            c = self.stdscr.getch()
            if c != -1: # Only handle input if a key was pressed
                running = self.handle_input(c)

def wrapper(stdscr):
    tui = GitTUI(stdscr)
    tui.main_loop()

if __name__ == "__main__":
    curses.wrapper(wrapper)
