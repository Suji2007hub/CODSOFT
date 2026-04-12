

from flask import Flask, render_template_string, request, jsonify
import copy
import random
import time
from typing import List, Tuple, Optional
from enum import Enum
from dataclasses import dataclass

# ---------------------- Game Core --------------------------
class Player(Enum):
    X = "X"
    O = "O"
    def opposite(self):
        return Player.X if self == Player.O else Player.O

class Difficulty(Enum):
    EASY = "easy"
    MEDIUM = "medium"
    HARD = "hard"
    UNBEATABLE = "unbeatable"

@dataclass
class MoveScore:
    position: int
    score: int
    depth: int

@dataclass
class ThinkingTrace:
    move: int
    score: int
    nodes_evaluated: int
    branches_pruned: int
    max_depth_reached: int
    evaluation_time_ms: float
    all_scores: List[MoveScore]

class TicTacToeGame:
    def __init__(self):
        self.board = [' ' for _ in range(9)]
        self.current_winner = None
    def make_move(self, position, player):
        if self.board[position] == ' ':
            self.board[position] = player.value
            if self.check_winner(position, player):
                self.current_winner = player
            return True
        return False
    def check_winner(self, position, player):
        row, col = position // 3, position % 3
        if all(self.board[row*3+i] == player.value for i in range(3)): return True
        if all(self.board[col+i*3] == player.value for i in range(3)): return True
        if position % 2 == 0:
            if all(self.board[i] == player.value for i in [0,4,8]): return True
            if all(self.board[i] == player.value for i in [2,4,6]): return True
        return False
    def get_empty_cells(self):
        return [i for i, v in enumerate(self.board) if v == ' ']
    def is_full(self):
        return ' ' not in self.board
    def reset(self):
        self.board = [' ' for _ in range(9)]
        self.current_winner = None

class MinimaxAI:
    def __init__(self, difficulty=Difficulty.HARD):
        self.difficulty = difficulty
        self.nodes_evaluated = 0
        self.branches_pruned = 0
        self.max_depth_reached = 0

    def get_move(self, game, ai_player):
        start = time.time()
        empty = game.get_empty_cells()
        if self.difficulty == Difficulty.EASY:
            move = random.choice(empty)
            trace = ThinkingTrace(move, 0, 0, 0, 0, (time.time()-start)*1000, [MoveScore(move,0,0)])
        elif self.difficulty == Difficulty.MEDIUM:
            move, score, scores = self._one_ply(game, ai_player)
            trace = ThinkingTrace(move, score, len(empty), 0, 1, (time.time()-start)*1000, scores)
        elif self.difficulty == Difficulty.HARD:
            self.nodes_evaluated = 0
            move, score, scores = self._minimax(game, 0, ai_player, ai_player, float('-inf'), float('inf'), True)
            trace = ThinkingTrace(move, score, self.nodes_evaluated, 0, self.max_depth_reached, (time.time()-start)*1000, scores)
        else:
            self.nodes_evaluated = 0
            self.branches_pruned = 0
            move, score, scores = self._minimax_ab(game, 0, ai_player, ai_player, float('-inf'), float('inf'), True)
            trace = ThinkingTrace(move, score, self.nodes_evaluated, self.branches_pruned, self.max_depth_reached, (time.time()-start)*1000, scores)
        return move, trace

    def _one_ply(self, game, ai_player):
        best_score = -1e9
        best_move = None
        scores = []
        for m in game.get_empty_cells():
            g = copy.deepcopy(game)
            g.make_move(m, ai_player)
            if g.current_winner == ai_player:
                score = 10
            else:
                human_win = False
                for hm in g.get_empty_cells():
                    hg = copy.deepcopy(g)
                    hg.make_move(hm, ai_player.opposite())
                    if hg.current_winner == ai_player.opposite():
                        human_win = True
                        break
                score = -10 if human_win else 0
            scores.append(MoveScore(m, score, 1))
            if score > best_score:
                best_score = score
                best_move = m
        return best_move, best_score, scores

    def _minimax(self, game, depth, curr, ai, alpha, beta, return_scores):
        self.nodes_evaluated += 1
        self.max_depth_reached = max(self.max_depth_reached, depth)
        if game.current_winner == ai: return None, 10-depth, None
        if game.current_winner == ai.opposite(): return None, depth-10, None
        if game.is_full(): return None, 0, None
        if curr == ai:
            best = -1e9
            best_move = None
            scores = [] if return_scores else None
            for m in game.get_empty_cells():
                g = copy.deepcopy(game)
                g.make_move(m, curr)
                _, score, _ = self._minimax(g, depth+1, curr.opposite(), ai, alpha, beta, False)
                if return_scores:
                    scores.append(MoveScore(m, score, depth))
                if score > best:
                    best = score
                    best_move = m
            return best_move, best, scores
        else:
            best = 1e9
            best_move = None
            scores = [] if return_scores else None
            for m in game.get_empty_cells():
                g = copy.deepcopy(game)
                g.make_move(m, curr)
                _, score, _ = self._minimax(g, depth+1, curr.opposite(), ai, alpha, beta, False)
                if return_scores:
                    scores.append(MoveScore(m, score, depth))
                if score < best:
                    best = score
                    best_move = m
            return best_move, best, scores

    def _minimax_ab(self, game, depth, curr, ai, alpha, beta, return_scores):
        self.nodes_evaluated += 1
        self.max_depth_reached = max(self.max_depth_reached, depth)
        if game.current_winner == ai: return None, 10-depth, None
        if game.current_winner == ai.opposite(): return None, depth-10, None
        if game.is_full(): return None, 0, None
        if curr == ai:
            best = -1e9
            best_move = None
            scores = [] if return_scores else None
            for m in game.get_empty_cells():
                g = copy.deepcopy(game)
                g.make_move(m, curr)
                _, score, _ = self._minimax_ab(g, depth+1, curr.opposite(), ai, alpha, beta, False)
                if return_scores:
                    scores.append(MoveScore(m, score, depth))
                if score > best:
                    best = score
                    best_move = m
                alpha = max(alpha, score)
                if beta <= alpha:
                    self.branches_pruned += 1
                    break
            return best_move, best, scores
        else:
            best = 1e9
            best_move = None
            scores = [] if return_scores else None
            for m in game.get_empty_cells():
                g = copy.deepcopy(game)
                g.make_move(m, curr)
                _, score, _ = self._minimax_ab(g, depth+1, curr.opposite(), ai, alpha, beta, False)
                if return_scores:
                    scores.append(MoveScore(m, score, depth))
                if score < best:
                    best = score
                    best_move = m
                beta = min(beta, score)
                if beta <= alpha:
                    self.branches_pruned += 1
                    break
            return best_move, best, scores

# ---------------------- Flask App --------------------------
app = Flask(__name__)

HTML_UI = """
<!DOCTYPE html>
<html>
<head><meta charset="UTF-8"><title>Tic-Tac-Toe AI</title>
<style>
*{box-sizing:border-box;} body{font-family:sans-serif; background:#1a2a3a; display:flex; justify-content:center; align-items:center; min-height:100vh; margin:0; padding:20px;}
.game-card{background:#fef9e8; border-radius:32px; padding:24px; max-width:500px; width:100%; text-align:center;}
.board{display:grid; grid-template-columns:repeat(3,1fr); gap:12px; background:#2d3e4b; padding:12px; border-radius:28px; margin-bottom:20px;}
.cell{aspect-ratio:1; background:#fef9e8; border-radius:20px; display:flex; align-items:center; justify-content:center; font-size:3rem; font-weight:bold; cursor:pointer;}
.cell.X{color:#2c6e9e;} .cell.O{color:#d97706;}
.status{background:#e9edf2; border-radius:60px; padding:10px; margin-bottom:20px; font-weight:bold;}
select,button{padding:8px 16px; border-radius:40px; border:none; font-weight:bold; margin:5px;}
.trace{background:#eef2f5; border-radius:24px; padding:12px; font-size:0.7rem; font-family:monospace; text-align:left; margin-top:12px;}
</style>
</head>
<body>
<div class="game-card">
    <h2>⚡ Tic-Tac-Toe AI</h2>
    <div class="status" id="statusMsg">Your turn (X)</div>
    <div class="board" id="board"></div>
    <div><label>Difficulty:</label>
    <select id="difficultySelect">
        <option value="0">Easy</option><option value="1">Medium</option><option value="2" selected>Hard</option><option value="3">Unbeatable</option>
    </select>
    <button id="resetBtn">New Game</button></div>
    <div class="trace" id="tracePanel"><p>AI reasoning will appear</p></div>
</div>
<script>
let board=Array(9).fill(' '), gameActive=true, currentPlayer='X', difficulty=2;
const statusDiv=document.getElementById('statusMsg'), boardDiv=document.getElementById('board'), tracePanel=document.getElementById('tracePanel');
function renderBoard(){
    boardDiv.innerHTML='';
    for(let i=0;i<9;i++){
        let cell=document.createElement('div');
        cell.classList.add('cell');
        if(board[i]==='X') cell.classList.add('X');
        if(board[i]==='O') cell.classList.add('O');
        cell.textContent=board[i]===' '?'':board[i];
        cell.onclick=()=>handleHuman(i);
        boardDiv.appendChild(cell);
    }
}
function checkWinner(b,p){ const w=[[0,1,2],[3,4,5],[6,7,8],[0,3,6],[1,4,7],[2,5,8],[0,4,8],[2,4,6]]; return w.some(line=>line.every(i=>b[i]===p)); }
function isDraw(b){ return b.every(c=>c!==' '); }
function updateStatus(){
    if(checkWinner(board,'X')){ statusDiv.innerText='You win!'; gameActive=false; }
    else if(checkWinner(board,'O')){ statusDiv.innerText='AI wins!'; gameActive=false; }
    else if(isDraw(board)){ statusDiv.innerText='Draw!'; gameActive=false; }
    else statusDiv.innerText=currentPlayer==='X'?'Your turn (X)':'AI thinking...';
}
async function requestAI(){
    if(!gameActive||currentPlayer!=='O') return;
    tracePanel.innerHTML='<p>⏳ AI computing...</p>';
    let res=await fetch('/ai_move',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({board,difficulty:parseInt(document.getElementById('difficultySelect').value)})});
    let data=await res.json();
    if(data.move!==undefined && board[data.move]===' '){
        board[data.move]='O';
        renderBoard();
        tracePanel.innerHTML=`<p>🧠 Move ${data.move} (score ${data.score})<br>🔍 Nodes:${data.nodes_evaluated} ✂️ Pruned:${data.branches_pruned}<br>📊 Scores: ${(data.move_scores||[]).map(m=>`${m.position}:${m.score}`).join(', ')}</p>`;
        if(checkWinner(board,'O')){ statusDiv.innerText='AI wins!'; gameActive=false; renderBoard(); return; }
        if(isDraw(board)){ statusDiv.innerText='Draw!'; gameActive=false; renderBoard(); return; }
        currentPlayer='X'; updateStatus(); renderBoard();
    }
}
async function handleHuman(idx){
    if(!gameActive||currentPlayer!=='X'||board[idx]!==' ') return;
    board[idx]='X'; renderBoard();
    if(checkWinner(board,'X')){ statusDiv.innerText='You win!'; gameActive=false; return; }
    if(isDraw(board)){ statusDiv.innerText='Draw!'; gameActive=false; return; }
    currentPlayer='O'; updateStatus(); renderBoard();
    await requestAI();
}
function resetGame(){
    board=Array(9).fill(' '); gameActive=true; currentPlayer='X'; difficulty=parseInt(document.getElementById('difficultySelect').value);
    renderBoard(); updateStatus(); tracePanel.innerHTML='<p>New game. AI ready.</p>';
}
document.getElementById('difficultySelect').onchange=()=>resetGame();
document.getElementById('resetBtn').onclick=resetGame;
resetGame();
</script>
</body>
</html>
"""

@app.route('/')
def home():
    return render_template_string(HTML_UI)

@app.route('/ai_move', methods=['POST'])
def ai_move():
    data = request.json
    board_raw = data.get('board')
    diff_idx = data.get('difficulty', 2)
    if not isinstance(board_raw, list) or len(board_raw) != 9:
        return jsonify({'error': 'Invalid board'}), 400
    board_norm = [' ' if c in (None, '', ' ') else c for c in board_raw]
    game = TicTacToeGame()
    game.board = board_norm
    diff_map = [Difficulty.EASY, Difficulty.MEDIUM, Difficulty.HARD, Difficulty.UNBEATABLE]
    ai = MinimaxAI(diff_map[diff_idx])
    move, trace = ai.get_move(game, Player.O)
    return jsonify({
        'move': move,
        'score': trace.score,
        'nodes_evaluated': trace.nodes_evaluated,
        'branches_pruned': trace.branches_pruned,
        'max_depth': trace.max_depth_reached,
        'evaluation_time': trace.evaluation_time_ms,
        'move_scores': [{'position': ms.position, 'score': ms.score, 'depth': ms.depth} for ms in trace.all_scores]
    })

if __name__ == '__main__':
    app.run(debug=True, port=5001)