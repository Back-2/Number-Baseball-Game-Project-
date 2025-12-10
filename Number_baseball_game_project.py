import random
from tkinter import *
from tkinter import messagebox
from datetime import datetime
import json
import os

SCORE_FILE = "scoreboard.txt"
LEADERBOARD_FILE = "leaderboard.txt"
SETTINGS_FILE = "settings.json"

# ==================== 설정 관리 ====================
def load_settings():
    """설정 파일에서 난이도 정보 로드"""
    default_settings = {
        "digits": 3,
        "max_attempts": 9
    }
    try:
        if os.path.exists(SETTINGS_FILE):
            with open(SETTINGS_FILE, "r", encoding="utf-8") as f:
                settings = json.load(f)
                return settings
    except:
        pass
    return default_settings

def save_settings(settings):
    """설정 파일에 난이도 정보 저장"""
    try:
        with open(SETTINGS_FILE, "w", encoding="utf-8") as f:
            json.dump(settings, f, ensure_ascii=False, indent=2)
    except:
        pass

# ==================== 리더보드 관리 ====================
def load_leaderboard():
    """리더보드 파일에서 데이터 로드 (리스트 구조로 변경)"""
    data = []
    try:
        f = open(LEADERBOARD_FILE, "r", encoding="utf-8")
        for line in f:
            line = line.strip()
            if not line:
                continue
            parts = line.split(",", 1)
            if len(parts) != 2:
                continue
            name, attempts_text = parts
            try:
                attempts = int(attempts_text)
                data.append((name, attempts))  # 튜플로 저장
            except ValueError:
                continue
        f.close()
    except FileNotFoundError:
        pass
    return data

def save_leaderboard():
    """리더보드 파일에 데이터 저장"""
    f = open(LEADERBOARD_FILE, "w", encoding="utf-8")
    for name, attempts in leaderboard:
        f.write("{0},{1}\n".format(name, attempts))
    f.close()

leaderboard = load_leaderboard()
settings = load_settings()

# ==================== 게임 로직 함수 ====================
def is_valid_guess(guess, n):
    """입력값 검증"""
    if len(guess) != n:
        return False, "{0}자리 숫자로 입력하세요.".format(n)
    
    if not guess.isdigit():
        return False, "숫자만 입력하세요."
    
    if guess[0] == "0":
        return False, "첫 자리는 0이 될 수 없습니다."
    
    if len(set(guess)) != len(guess):
        return False, "중복된 숫자가 있습니다."
    
    return True, ""

def generate_secret(n_digits):
    """n자리 비밀 숫자 생성"""
    if n_digits == 3:
        digits = list(range(1, 10))
        first = random.choice(digits)
        digits.remove(first)
        second = random.choice(digits)
        digits.remove(second)
        third = random.choice(digits)
        return str(first) + str(second) + str(third)
    elif n_digits == 4:
        digits = list(range(1, 10))
        first = random.choice(digits)
        digits.remove(first)
        second = random.choice(digits)
        digits.remove(second)
        third = random.choice(digits)
        digits.remove(third)
        fourth = random.choice(digits)
        return str(first) + str(second) + str(third) + str(fourth)
    return ""

def calculate_strike_ball(secret, guess):
    """스트라이크와 볼 계산"""
    max_len = min(len(secret), len(guess))
    strike = 0
    for i in range(max_len):
        if secret[i] == guess[i]:
            strike += 1
    
    ball = 0
    for i, digit in enumerate(guess):
        if digit in secret:
            if i >= len(secret) or secret[i] != digit:
                ball += 1
    
    return strike, ball

def save_score(name, win, attempts=None):
    """게임 결과를 파일에 저장"""
    now = datetime.now()
    date_str = now.strftime("%Y-%m-%d")
    result = "승" if win else "패"
    line = "{0} - {1} ({2})\n".format(name, result, date_str)
    
    f = open(SCORE_FILE, "a", encoding="utf-8")
    f.write(line)
    f.close()
    
    # 리더보드에 저장 (승리한 경우만, 같은 이름도 여러 번 저장 가능)
    if win and attempts is not None:
        # 리더보드에 추가 (같은 이름이 여러 번 나타날 수 있음)
        leaderboard.append((name, attempts))
        save_leaderboard()

# ==================== GUI 클래스 ====================
class NumberBaseballGame:
    def __init__(self, root):
        self.root = root
        self.root.title("숫자야구 게임")
        self.root.geometry("400x500")
        
        # 게임 상태 변수
        self.secret = ""
        self.attempts = 0
        self.max_attempts = settings.get("max_attempts", 9)
        self.n_digits = settings.get("digits", 3)
        self.player_name = ""
        self.current_player = 1  # 1 또는 2
        self.two_player_mode = False
        self.player1_name = ""
        self.player2_name = ""
        self.player1_attempts = 0
        self.player2_attempts = 0
        self.hint_given = False
        
        self.show_main_screen()
    
    def clear_window(self):
        """윈도우의 모든 위젯 제거"""
        for widget in self.root.winfo_children():
            widget.destroy()
    
    def show_main_screen(self):
        """메인 화면 표시 (이름 입력, 게임 시작)"""
        self.clear_window()
        
        # 제목
        title_label = Label(self.root, text="=== 숫자야구 게임 ===", font=("Arial", 16, "bold"))
        title_label.pack(pady=20)
        
        # 난이도 선택 (3개 맞추기 / 4개 맞추기)
        difficulty_frame = Frame(self.root)
        difficulty_frame.pack(pady=10)
        Label(difficulty_frame, text="난이도:", font=("Arial", 12)).pack(side=LEFT, padx=5)
        self.difficulty_var = IntVar(value=self.n_digits)
        Radiobutton(difficulty_frame, text="3개 맞추기", variable=self.difficulty_var, 
                   value=3, font=("Arial", 11), command=self.update_difficulty).pack(side=LEFT, padx=5)
        Radiobutton(difficulty_frame, text="4개 맞추기", variable=self.difficulty_var, 
                   value=4, font=("Arial", 11), command=self.update_difficulty).pack(side=LEFT, padx=5)
        
        # 이름 입력
        name_frame = Frame(self.root)
        name_frame.pack(pady=10)
        Label(name_frame, text="이름:", font=("Arial", 12)).pack(side=LEFT, padx=5)
        self.name_entry = Entry(name_frame, width=20, font=("Arial", 12))
        self.name_entry.pack(side=LEFT, padx=5)
        
        # 게임 시작 버튼
        start_btn = Button(self.root, text="게임 시작", font=("Arial", 12), 
                          command=self.start_game, width=15, height=2)
        start_btn.pack(pady=15)
        
        # 2인 플레이 버튼
        two_player_btn = Button(self.root, text="2인 플레이", font=("Arial", 12),
                               command=self.start_two_player_game, width=15, height=2)
        two_player_btn.pack(pady=5)
        
        # 설정 버튼
        settings_btn = Button(self.root, text="설정", font=("Arial", 10),
                             command=self.show_settings, width=15)
        settings_btn.pack(pady=5)
        
        # 리더보드 버튼
        leaderboard_btn = Button(self.root, text="리더보드", font=("Arial", 10),
                                command=self.show_leaderboard_dialog, width=15)
        leaderboard_btn.pack(pady=5)
        
        # 종료 버튼
        exit_btn = Button(self.root, text="종료", font=("Arial", 10),
                         command=self.quit_application, width=15)
        exit_btn.pack(pady=5)
    
    def update_difficulty(self):
        """난이도 선택 업데이트"""
        self.n_digits = self.difficulty_var.get()
        # 설정 파일에도 저장
        global settings
        settings["digits"] = self.n_digits
        save_settings(settings)
    
    def show_settings(self):
        """설정 화면 표시 (난이도 제외, 최대 시도수만)"""
        settings_window = Toplevel(self.root)
        settings_window.title("설정")
        settings_window.geometry("300x150")
        
        Label(settings_window, text="설정", font=("Arial", 14, "bold")).pack(pady=10)
        
        # 최대 시도수 선택
        attempts_frame = Frame(settings_window)
        attempts_frame.pack(pady=10)
        Label(attempts_frame, text="최대 시도수:").pack(side=LEFT, padx=5)
        self.max_attempts_var = IntVar(value=self.max_attempts)
        attempts_entry = Entry(attempts_frame, textvariable=self.max_attempts_var, width=10)
        attempts_entry.pack(side=LEFT, padx=5)
        
        def save_and_close():
            global settings
            settings["max_attempts"] = self.max_attempts_var.get()
            save_settings(settings)
            self.max_attempts = settings["max_attempts"]
            settings_window.destroy()
            messagebox.showinfo("설정", "설정이 저장되었습니다.")
        
        Button(settings_window, text="저장", command=save_and_close).pack(pady=10)
    
    def start_game(self):
        """1인 게임 시작"""
        self.player_name = self.name_entry.get().strip()
        if self.player_name == "":
            messagebox.showwarning("입력 오류", "이름을 입력하세요.")
            return
        
        self.two_player_mode = False
        self.attempts = 0
        self.hint_given = False
        self.secret = generate_secret(self.n_digits)
        self.show_game_screen()
    
    def start_two_player_game(self):
        """2인 게임 시작"""
        dialog = Toplevel(self.root)
        dialog.title("2인 플레이")
        dialog.geometry("400x250")
        
        # 난이도 선택 표시
        Label(dialog, text="난이도: {0}개 맞추기".format(self.n_digits), 
              font=("Arial", 11)).pack(pady=5)
        
        Label(dialog, text="플레이어 1 이름:", font=("Arial", 12)).pack(pady=8)
        p1_entry = Entry(dialog, width=25, font=("Arial", 12))
        p1_entry.pack(pady=5)
        
        Label(dialog, text="플레이어 2 이름:", font=("Arial", 12)).pack(pady=8)
        p2_entry = Entry(dialog, width=25, font=("Arial", 12))
        p2_entry.pack(pady=5)
        
        def start():
            p1_name = p1_entry.get().strip()
            p2_name = p2_entry.get().strip()
            if p1_name == "" or p2_name == "":
                messagebox.showwarning("입력 오류", "두 플레이어의 이름을 모두 입력하세요.")
                return
            
            self.two_player_mode = True
            self.player1_name = p1_name
            self.player2_name = p2_name
            self.player1_attempts = 0
            self.player2_attempts = 0
            self.current_player = 1
            self.attempts = 0
            self.hint_given = False
            self.secret = generate_secret(self.n_digits)
            dialog.destroy()
            self.show_game_screen()
        
        Button(dialog, text="시작", command=start, font=("Arial", 12), 
               width=15, height=2).pack(pady=15)
    
    def show_game_screen(self):
        """게임 진행 화면 표시"""
        self.clear_window()
        
        # 제목
        title_text = "=== 숫자야구 게임 ==="
        title_label = Label(self.root, text=title_text, font=("Arial", 16, "bold"))
        title_label.pack(pady=10)
        
        # 플레이어 정보
        if self.two_player_mode:
            current_name = self.player1_name if self.current_player == 1 else self.player2_name
            player_label = Label(self.root, text="{0}님, 시작하세요!".format(current_name), 
                               font=("Arial", 12))
            player_label.pack(pady=5)
        else:
            player_label = Label(self.root, text="{0}님, 시작하세요!".format(self.player_name), 
                               font=("Arial", 12))
            player_label.pack(pady=5)
        
        # 시도 횟수 표시
        self.attempts_label = Label(self.root, 
                                   text="시도: {0}/{1}".format(self.attempts, self.max_attempts),
                                   font=("Arial", 12))
        self.attempts_label.pack(pady=5)
        
        # 입력 필드
        input_frame = Frame(self.root)
        input_frame.pack(pady=10)
        Label(input_frame, text="숫자 입력:", font=("Arial", 12)).pack(side=LEFT, padx=5)
        self.guess_entry = Entry(input_frame, width=15, font=("Arial", 12))
        self.guess_entry.pack(side=LEFT, padx=5)
        self.guess_entry.bind("<Return>", lambda e: self.submit_guess())
        
        # 제출 버튼
        submit_btn = Button(self.root, text="제출", font=("Arial", 12),
                           command=self.submit_guess, width=15, height=2)
        submit_btn.pack(pady=10)
        
        # 결과 표시 영역
        self.result_label = Label(self.root, text="", font=("Arial", 14, "bold"), fg="blue")
        self.result_label.pack(pady=10)
        
        # 힌트 표시 영역
        self.hint_label = Label(self.root, text="", font=("Arial", 10), fg="red")
        self.hint_label.pack(pady=5)
        
        # 다시 시작 버튼 (게임 중에는 숨김)
        self.restart_btn = Button(self.root, text="다시 시작", font=("Arial", 10),
                                  command=self.show_main_screen, width=15)
        self.restart_btn.pack_forget()
        
        # 중간 종료 버튼
        quit_game_btn = Button(self.root, text="중간 종료", font=("Arial", 10),
                               command=self.quit_game, width=15, fg="red")
        quit_game_btn.pack(pady=5)
        
        # 종료 버튼
        exit_btn = Button(self.root, text="종료", font=("Arial", 10),
                         command=self.quit_application, width=15)
        exit_btn.pack(pady=5)
    
    def submit_guess(self):
        """입력값 제출 및 처리"""
        guess = self.guess_entry.get().strip()
        
        # 입력 검증
        ok, msg = is_valid_guess(guess, self.n_digits)
        if not ok:
            messagebox.showerror("입력 오류", msg)
            return
        
        self.attempts += 1
        
        # 스트라이크/볼 계산
        s, b = calculate_strike_ball(self.secret, guess)
        result_text = "{0}S {1}B".format(s, b)
        self.result_label.config(text=result_text)
        
        # 정답 확인
        if s == self.n_digits:
            # 성공
            if self.two_player_mode:
                if self.current_player == 1:
                    self.player1_attempts = self.attempts
                    self.current_player = 2
                    self.attempts = 0
                    self.guess_entry.delete(0, END)
                    self.result_label.config(text="")
                    self.hint_given = False  # 힌트 초기화
                    self.hint_label.config(text="")  # 힌트 라벨 초기화
                    messagebox.showinfo("성공", "{0}님이 {1}번 만에 맞췄습니다!\n{2}님 차례입니다.".format(
                        self.player1_name, self.player1_attempts, self.player2_name))
                    self.show_game_screen()
                    return
                else:
                    self.player2_attempts = self.attempts
                    # 두 플레이어 모두 완료
                    winner = self.player1_name if self.player1_attempts < self.player2_attempts else self.player2_name
                    if self.player1_attempts == self.player2_attempts:
                        result_msg = "무승부! 둘 다 {0}번 만에 맞췄습니다.".format(self.player1_attempts)
                    else:
                        result_msg = "{0}님이 승리했습니다! ({1}번 vs {2}번)".format(
                            winner, self.player1_attempts, self.player2_attempts)
                    
                    # 둘 다 리더보드에 저장 (둘 다 승리했으므로)
                    save_score(self.player1_name, True, self.player1_attempts)
                    save_score(self.player2_name, True, self.player2_attempts)
                    messagebox.showinfo("게임 종료", result_msg)
                    # 초기 화면으로 이동 후 리더보드 표시
                    self.show_main_screen()
                    self.root.after(100, self.show_leaderboard_dialog)  # 화면 전환 후 리더보드 표시
                    return
            
            # 1인 모드 성공
            save_score(self.player_name, True, self.attempts)
            messagebox.showinfo("성공", "정답! {0}번 만에 맞췄습니다.".format(self.attempts))
            # 초기 화면으로 이동 후 리더보드 표시
            self.show_main_screen()
            self.root.after(100, self.show_leaderboard_dialog)  # 화면 전환 후 리더보드 표시
            return
        
        # 시도 횟수 업데이트
        self.attempts_label.config(text="시도: {0}/{1}".format(self.attempts, self.max_attempts))
        
        # 힌트 제공 (5번째 시도 후)
        if self.attempts == 5 and not self.hint_given:
            hint_pos = random.randint(0, self.n_digits - 1)
            hint_text = "힌트: {0}번째 자리는 {1}입니다.".format(hint_pos + 1, self.secret[hint_pos])
            self.hint_label.config(text=hint_text)
            self.hint_given = True
        
        # 최대 시도수 초과
        if self.attempts >= self.max_attempts:
            if self.two_player_mode:
                if self.current_player == 1:
                    self.player1_attempts = self.max_attempts
                    self.current_player = 2
                    self.attempts = 0
                    self.guess_entry.delete(0, END)
                    self.result_label.config(text="")
                    self.hint_given = False  # 힌트 초기화
                    self.hint_label.config(text="")  # 힌트 라벨 초기화
                    messagebox.showinfo("실패", "{0}님 실패했습니다. 정답은 {1}입니다.\n{2}님 차례입니다.".format(
                        self.player1_name, self.secret, self.player2_name))
                    self.secret = generate_secret(self.n_digits)  # 새로운 정답 생성
                    self.show_game_screen()
                    return
                else:
                    self.player2_attempts = self.max_attempts
                    save_score(self.player1_name, False, self.player1_attempts)
                    save_score(self.player2_name, False, self.player2_attempts)
                    messagebox.showinfo("실패", "{0}님도 실패했습니다. 정답은 {1}입니다.".format(
                        self.player2_name, self.secret))
                    # 초기 화면으로 이동 후 리더보드 표시
                    self.show_main_screen()
                    self.root.after(100, self.show_leaderboard_dialog)  # 화면 전환 후 리더보드 표시
                    return
            
            # 1인 모드 실패
            save_score(self.player_name, False, self.attempts)
            messagebox.showinfo("실패", "실패했습니다. 정답은 {0}입니다.".format(self.secret))
            # 초기 화면으로 이동 후 리더보드 표시
            self.show_main_screen()
            self.root.after(100, self.show_leaderboard_dialog)  # 화면 전환 후 리더보드 표시
            return
        
        # 입력 필드 초기화
        self.guess_entry.delete(0, END)
    
    def quit_game(self):
        """게임 중간 종료 (리더보드에 기록하지 않음)"""
        msg = "게임을 중간에 종료하시겠습니까?\n(리더보드에 기록되지 않습니다)"
        title = "중간 종료"
        
        result = messagebox.askyesno(title, msg)
        if result:
            # 리더보드에 저장하지 않고 메인 화면으로 돌아감
            self.two_player_mode = False
            self.show_main_screen()
    
    def quit_application(self):
        """애플리케이션 종료"""
        result = messagebox.askyesno("종료", "프로그램을 종료하시겠습니까?")
        if result:
            self.root.quit()
            self.root.destroy()
    
    def show_leaderboard_dialog(self):
        """리더보드 다이얼로그 표시"""
        dialog = Toplevel(self.root)
        dialog.title("리더보드")
        dialog.geometry("300x250")
        
        Label(dialog, text="=== 리더보드 ===", font=("Arial", 14, "bold")).pack(pady=10)
        
        if not leaderboard:
            Label(dialog, text="데이터가 없습니다.", font=("Arial", 10)).pack(pady=20)
        else:
            # 시도 횟수가 적은 순으로 정렬 (리스트 구조)
            sorted_entries = sorted(leaderboard, key=lambda x: x[1])
            # 상위 3개만 표시 (같은 이름도 여러 번 나타날 수 있음)
            top_three = sorted_entries[:3]
            
            for idx, (name, attempts) in enumerate(top_three, 1):
                text = "{0}위: {1} - {2}회".format(idx, name, attempts)
                Label(dialog, text=text, font=("Arial", 11)).pack(pady=5)
        
        Button(dialog, text="확인", command=dialog.destroy, width=10).pack(pady=15)

# ==================== 메인 실행 ====================
if __name__ == "__main__":
    root = Tk()
    app = NumberBaseballGame(root)
    root.mainloop()
