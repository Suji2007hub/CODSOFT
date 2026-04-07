"""
game_core.py
Tic-Tac-Toe Game Engine with Minimax & Alpha-Beta Pruning

This module provides:
- Game state management (board, win detection)
- AI with 4 difficulty levels: Easy (random), Medium (1-ply), Hard (full Minimax), Unbeatable (Minimax + Alpha-Beta)
- ThinkingTrace dataclass to expose AI's internal reasoning (nodes evaluated, branches pruned, move scores)
"""

from typing import List, Tuple, Optional, Dict
from enum import Enum
from dataclasses import dataclass
import copy
import random
import time


class Player(Enum):
    """Game players: X (human) and O (AI)."""
    X = "X"
    O = "O"
    
    def opposite(self):
        """Return the other player."""
        return Player.X if self == Player.O else Player.O


class Difficulty(Enum):
    """AI difficulty levels with different algorithmic complexity."""
    EASY = "easy"           # Random moves – no intelligence
    MEDIUM = "medium"       # 1-ply lookahead – only immediate win/block
    HARD = "hard"           # Full Minimax – recursive evaluation of all possibilities
    UNBEATABLE = "unbeatable"  # Minimax + Alpha-Beta pruning – optimal and faster


@dataclass
class MoveScore:
    """Stores the score calculated for a single move (used for heatmap)."""
    position: int      # 0..8 board index
    score: int         # Numerical value (positive = good for AI, negative = bad)
    depth: int         # How deep in the recursion this score was computed
    is_pruned: bool = False  # (reserved) indicates if branch was cut by Alpha-Beta


@dataclass
class ThinkingTrace:
    """
    Complete record of the AI's decision process for one move.
    This is the "X-Ray" data – shows exactly what the algorithm did.
    """
    move: int                     # Chosen move
    score: int                    # Score of the chosen move
    nodes_evaluated: int          # Number of game states explored
    branches_pruned: int          # Number of branches cut by Alpha-Beta
    max_depth_reached: int        # Deepest recursion level
    evaluation_time_ms: float     # Time taken to decide (milliseconds)
    all_scores: List[MoveScore]   # Scores for every possible move (heatmap data)


class TicTacToeGame:
    """Core game logic: board, moves, win/draw detection."""
    
    def __init__(self):
        self.board = [' ' for _ in range(9)]   # Empty board: list of 9 chars
        self.current_winner = None             # Player who won (or None)
        self.winning_line = None               # Indices of the winning line (for UI highlight)
    
    def make_move(self, position: int, player: Player) -> bool:
        """Place a marker on the board if the cell is empty. Returns True on success."""
        if self.board[position] == ' ':
            self.board[position] = player.value
            if self.check_winner(position, player):
                self.current_winner = player
                self.winning_line = self.get_winning_line()
            return True
        return False
    
    def check_winner(self, position: int, player: Player) -> bool:
        """
        After a move at `position`, check if that move created a win.
        Uses row, column, and diagonal checks.
        """
        row = position // 3
        col = position % 3
        
        # Check row
        if all(self.board[row*3 + i] == player.value for i in range(3)):
            return True
        # Check column
        if all(self.board[col + i*3] == player.value for i in range(3)):
            return True
        # Check diagonals (only if position is on a diagonal)
        if position % 2 == 0:   # corners (0,2,6,8) or center (4)
            if all(self.board[i] == player.value for i in [0,4,8]):
                return True
            if all(self.board[i] == player.value for i in [2,4,6]):
                return True
        return False
    
    def get_winning_line(self) -> Optional[List[int]]:
        """Return the indices of the three cells that form a win (for visual highlight)."""
        win_patterns = [
            [0,1,2], [3,4,5], [6,7,8],  # rows
            [0,3,6], [1,4,7], [2,5,8],  # columns
            [0,4,8], [2,4,6]            # diagonals
        ]
        for pattern in win_patterns:
            if (self.board[pattern[0]] == self.board[pattern[1]] == 
                self.board[pattern[2]] != ' '):
                return pattern
        return None
    
    def get_empty_cells(self) -> List[int]:
        """Return list of indices where board is empty."""
        return [i for i, val in enumerate(self.board) if val == ' ']
    
    def is_full(self) -> bool:
        """Return True if no empty cells remain."""
        return ' ' not in self.board
    
    def reset(self):
        """Reset the game to initial state."""
        self.board = [' ' for _ in range(9)]
        self.current_winner = None
        self.winning_line = None


class MinimaxAI:
    """
    AI player using Minimax with optional Alpha-Beta pruning.
    The difficulty level determines which algorithm is used.
    """
    
    def __init__(self, difficulty: Difficulty = Difficulty.HARD):
        self.difficulty = difficulty
        self.nodes_evaluated = 0      # counter for current move
        self.branches_pruned = 0
        self.max_depth_reached = 0
        self.last_trace = None
    
    def get_move(self, game: TicTacToeGame, ai_player: Player) -> Tuple[int, ThinkingTrace]:
        """
        Return (chosen_move, ThinkingTrace) based on the current difficulty.
        Also records timing and statistics.
        """
        start_time = time.time()
        empty_cells = game.get_empty_cells()
        
        if self.difficulty == Difficulty.EASY:
            # Random move – no search
            move = random.choice(empty_cells)
            trace = ThinkingTrace(
                move=move, score=0, nodes_evaluated=0, branches_pruned=0,
                max_depth_reached=0, evaluation_time_ms=(time.time()-start_time)*1000,
                all_scores=[MoveScore(position=move, score=0, depth=0)]
            )
        
        elif self.difficulty == Difficulty.MEDIUM:
            # 1-ply lookahead: only immediate win/block
            move, score, all_scores = self._one_ply_lookahead(game, ai_player)
            trace = ThinkingTrace(
                move=move, score=score, nodes_evaluated=len(empty_cells),
                branches_pruned=0, max_depth_reached=1,
                evaluation_time_ms=(time.time()-start_time)*1000, all_scores=all_scores
            )
        
        elif self.difficulty == Difficulty.HARD:
            # Full Minimax (no pruning)
            self.nodes_evaluated = 0
            move, score, all_scores = self._minimax(
                game, 0, ai_player, ai_player, float('-inf'), float('inf'),
                return_all_scores=True
            )
            trace = ThinkingTrace(
                move=move, score=score, nodes_evaluated=self.nodes_evaluated,
                branches_pruned=self.branches_pruned, max_depth_reached=self.max_depth_reached,
                evaluation_time_ms=(time.time()-start_time)*1000, all_scores=all_scores
            )
        
        else:  # UNBEATABLE – Minimax with Alpha-Beta pruning
            self.nodes_evaluated = 0
            self.branches_pruned = 0
            move, score, all_scores = self._minimax_alpha_beta(
                game, 0, ai_player, ai_player, float('-inf'), float('inf'),
                return_all_scores=True
            )
            trace = ThinkingTrace(
                move=move, score=score, nodes_evaluated=self.nodes_evaluated,
                branches_pruned=self.branches_pruned, max_depth_reached=self.max_depth_reached,
                evaluation_time_ms=(time.time()-start_time)*1000, all_scores=all_scores
            )
        
        self.last_trace = trace
        return move, trace
    
    def _one_ply_lookahead(self, game: TicTacToeGame, ai_player: Player) -> Tuple[int, int, List[MoveScore]]:
        """
        Evaluate only immediate next moves:
        - +10 if AI can win now
        - -10 if human can win on their next turn
        - 0 otherwise
        """
        best_score = float('-inf')
        best_move = None
        all_scores = []
        
        for move in game.get_empty_cells():
            # Simulate AI move
            game_copy = copy.deepcopy(game)
            game_copy.make_move(move, ai_player)
            
            if game_copy.current_winner == ai_player:
                score = 10
            else:
                # Check if human can win immediately after
                human_win = False
                for human_move in game_copy.get_empty_cells():
                    test_copy = copy.deepcopy(game_copy)
                    test_copy.make_move(human_move, ai_player.opposite())
                    if test_copy.current_winner == ai_player.opposite():
                        human_win = True
                        break
                score = -10 if human_win else 0
            
            all_scores.append(MoveScore(position=move, score=score, depth=1))
            if score > best_score:
                best_score = score
                best_move = move
        
        return best_move, best_score, all_scores
    
    def _minimax(self, game: TicTacToeGame, depth: int, current_player: Player,
                 ai_player: Player, alpha: float, beta: float,
                 return_all_scores: bool = False) -> Tuple[Optional[int], int, Optional[List[MoveScore]]]:
        """
        Pure Minimax (no pruning). Returns (best_move, score, all_scores).
        The alpha, beta parameters are ignored but kept for signature compatibility.
        """
        self.nodes_evaluated += 1
        self.max_depth_reached = max(self.max_depth_reached, depth)
        
        # Terminal state evaluation
        if game.current_winner == ai_player:
            return None, 10 - depth, None           # AI wins – prefer faster wins
        if game.current_winner == ai_player.opposite():
            return None, depth - 10, None           # Human wins – delay loss
        if game.is_full():
            return None, 0, None                    # Draw
        
        if current_player == ai_player:
            # Maximizing player (AI)
            best_score = float('-inf')
            best_move = None
            all_scores = [] if return_all_scores else None
            
            for move in game.get_empty_cells():
                game_copy = copy.deepcopy(game)
                game_copy.make_move(move, current_player)
                _, score, _ = self._minimax(
                    game_copy, depth+1, current_player.opposite(),
                    ai_player, alpha, beta, False
                )
                if return_all_scores:
                    all_scores.append(MoveScore(position=move, score=score, depth=depth))
                if score > best_score:
                    best_score = score
                    best_move = move
            return best_move, best_score, all_scores
        
        else:
            # Minimizing player (human)
            best_score = float('inf')
            best_move = None
            all_scores = [] if return_all_scores else None
            
            for move in game.get_empty_cells():
                game_copy = copy.deepcopy(game)
                game_copy.make_move(move, current_player)
                _, score, _ = self._minimax(
                    game_copy, depth+1, current_player.opposite(),
                    ai_player, alpha, beta, False
                )
                if return_all_scores:
                    all_scores.append(MoveScore(position=move, score=score, depth=depth))
                if score < best_score:
                    best_score = score
                    best_move = move
            return best_move, best_score, all_scores
    
    def _minimax_alpha_beta(self, game: TicTacToeGame, depth: int, current_player: Player,
                            ai_player: Player, alpha: float, beta: float,
                            return_all_scores: bool = False) -> Tuple[Optional[int], int, Optional[List[MoveScore]]]:
        """
        Minimax with Alpha-Beta pruning.
        - alpha: best score maximizing player can guarantee
        - beta:  best score minimizing player can guarantee
        Pruning occurs when alpha >= beta.
        """
        self.nodes_evaluated += 1
        self.max_depth_reached = max(self.max_depth_reached, depth)
        
        # Terminal evaluation (same as pure Minimax)
        if game.current_winner == ai_player:
            return None, 10 - depth, None
        if game.current_winner == ai_player.opposite():
            return None, depth - 10, None
        if game.is_full():
            return None, 0, None
        
        if current_player == ai_player:
            # Maximizing
            best_score = float('-inf')
            best_move = None
            all_scores = [] if return_all_scores else None
            
            for move in game.get_empty_cells():
                game_copy = copy.deepcopy(game)
                game_copy.make_move(move, current_player)
                _, score, _ = self._minimax_alpha_beta(
                    game_copy, depth+1, current_player.opposite(),
                    ai_player, alpha, beta, False
                )
                if return_all_scores:
                    all_scores.append(MoveScore(position=move, score=score, depth=depth))
                
                if score > best_score:
                    best_score = score
                    best_move = move
                
                # Alpha update and prune check
                alpha = max(alpha, score)
                if beta <= alpha:
                    self.branches_pruned += 1
                    break   # prune remaining moves
            return best_move, best_score, all_scores
        
        else:
            # Minimizing
            best_score = float('inf')
            best_move = None
            all_scores = [] if return_all_scores else None
            
            for move in game.get_empty_cells():
                game_copy = copy.deepcopy(game)
                game_copy.make_move(move, current_player)
                _, score, _ = self._minimax_alpha_beta(
                    game_copy, depth+1, current_player.opposite(),
                    ai_player, alpha, beta, False
                )
                if return_all_scores:
                    all_scores.append(MoveScore(position=move, score=score, depth=depth))
                
                if score < best_score:
                    best_score = score
                    best_move = move
                
                # Beta update and prune check
                beta = min(beta, score)
                if beta <= alpha:
                    self.branches_pruned += 1
                    break
            return best_move, best_score, all_scores
    
    def get_move_scores_for_display(self, game: TicTacToeGame, ai_player: Player) -> List[MoveScore]:
        """
        Public method to get scores for all empty cells (used by frontend heatmap).
        It temporarily resets counters to avoid interfering with actual move decision.
        """
        if self.difficulty == Difficulty.EASY:
            return [MoveScore(pos, 0, 0) for pos in game.get_empty_cells()]
        
        if self.difficulty == Difficulty.MEDIUM:
            _, _, scores = self._one_ply_lookahead(game, ai_player)
            return scores
        
        # For HARD and UNBEATABLE, we call the respective algorithms with return_all_scores=True
        old_nodes = self.nodes_evaluated
        old_pruned = self.branches_pruned
        self.nodes_evaluated = 0
        
        if self.difficulty == Difficulty.HARD:
            _, _, scores = self._minimax(
                game, 0, ai_player, ai_player, float('-inf'), float('inf'),
                return_all_scores=True
            )
        else:  # UNBEATABLE
            _, _, scores = self._minimax_alpha_beta(
                game, 0, ai_player, ai_player, float('-inf'), float('inf'),
                return_all_scores=True
            )
        
        self.nodes_evaluated = old_nodes
        self.branches_pruned = old_pruned
        return scores if scores else []