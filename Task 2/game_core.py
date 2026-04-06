"""
Tic-Tac-Toe Game Engine with Minimax & Alpha-Beta Pruning
Clean, modular, testable architecture
"""

from typing import List, Tuple, Optional, Dict
from enum import Enum
from dataclasses import dataclass, field
import copy


class Player(Enum):
    """Game players"""
    X = "X"  # Human
    O = "O"  # AI
    
    def opposite(self):
        return Player.X if self == Player.O else Player.O


class Difficulty(Enum):
    """AI difficulty levels"""
    EASY = "easy"           # Random moves
    MEDIUM = "medium"       # 1-ply lookahead
    HARD = "hard"           # Full Minimax
    UNBEATABLE = "unbeatable"  # Minimax + Alpha-Beta


@dataclass
class MoveScore:
    """Represents a move with its calculated score"""
    position: int
    score: int
    depth: int
    is_pruned: bool = False


@dataclass
class ThinkingTrace:
    """Records AI's decision-making process"""
    move: int
    score: int
    nodes_evaluated: int
    branches_pruned: int
    max_depth_reached: int
    evaluation_time_ms: float
    all_scores: List[MoveScore]


class TicTacToeGame:
    """Core game logic and state management"""
    
    def __init__(self):
        self.board = [' ' for _ in range(9)]
        self.current_winner = None
        self.winning_line = None
    
    def display_board(self) -> str:
        """Return visual representation of board"""
        rows = []
        for i in range(0, 9, 3):
            rows.append(' | '.join(self.board[i:i+3]))
            if i < 6:
                rows.append('---------')
        return '\n'.join(rows)
    
    def make_move(self, position: int, player: Player) -> bool:
        """Place a marker on the board"""
        if self.board[position] == ' ':
            self.board[position] = player.value
            if self.check_winner(position, player):
                self.current_winner = player
                self.winning_line = self.get_winning_line()
            return True
        return False
    
    def check_winner(self, position: int, player: Player) -> bool:
        """Check if the last move created a win"""
        row = position // 3
        col = position % 3
        
        # Check row
        if all(self.board[row*3 + i] == player.value for i in range(3)):
            self.winning_line = [(row*3, row*3+1, row*3+2)]
            return True
        
        # Check column
        if all(self.board[col + i*3] == player.value for i in range(3)):
            self.winning_line = [(col, col+3, col+6)]
            return True
        
        # Check diagonals
        if position % 2 == 0:  # Only center or corners can be on diagonals
            if all(self.board[i] == player.value for i in [0, 4, 8]):
                self.winning_line = [(0, 4, 8)]
                return True
            if all(self.board[i] == player.value for i in [2, 4, 6]):
                self.winning_line = [(2, 4, 6)]
                return True
        
        return False
    
    def get_winning_line(self) -> Optional[List[int]]:
        """Return the winning line coordinates"""
        # Check all possible winning combinations
        win_patterns = [
            [0,1,2], [3,4,5], [6,7,8],  # Rows
            [0,3,6], [1,4,7], [2,5,8],  # Columns
            [0,4,8], [2,4,6]            # Diagonals
        ]
        for pattern in win_patterns:
            if (self.board[pattern[0]] == self.board[pattern[1]] == 
                self.board[pattern[2]] != ' '):
                return pattern
        return None
    
    def get_empty_cells(self) -> List[int]:
        """Return list of available positions"""
        return [i for i, val in enumerate(self.board) if val == ' ']
    
    def is_full(self) -> bool:
        """Check if board is full"""
        return ' ' not in self.board
    
    def reset(self):
        """Reset game state"""
        self.board = [' ' for _ in range(9)]
        self.current_winner = None
        self.winning_line = None


class MinimaxAI:
    """AI player using Minimax algorithm with Alpha-Beta pruning"""
    
    def __init__(self, difficulty: Difficulty = Difficulty.HARD):
        self.difficulty = difficulty
        self.nodes_evaluated = 0
        self.branches_pruned = 0
        self.max_depth_reached = 0
        self.last_trace = None
    
    def get_move(self, game: TicTacToeGame, ai_player: Player) -> Tuple[int, ThinkingTrace]:
        """Get AI move based on current difficulty"""
        import time
        start_time = time.time()
        
        empty_cells = game.get_empty_cells()
        
        if self.difficulty == Difficulty.EASY:
            # Random move
            import random
            move = random.choice(empty_cells)
            trace = ThinkingTrace(
                move=move,
                score=0,
                nodes_evaluated=0,
                branches_pruned=0,
                max_depth_reached=0,
                evaluation_time_ms=(time.time() - start_time) * 1000,
                all_scores=[MoveScore(position=move, score=0, depth=0)]
            )
        
        elif self.difficulty == Difficulty.MEDIUM:
            # 1-ply lookahead
            move, score, all_scores = self._one_ply_lookahead(game, ai_player)
            trace = ThinkingTrace(
                move=move,
                score=score,
                nodes_evaluated=len(empty_cells),
                branches_pruned=0,
                max_depth_reached=1,
                evaluation_time_ms=(time.time() - start_time) * 1000,
                all_scores=all_scores
            )
        
        elif self.difficulty == Difficulty.HARD:
            # Full Minimax
            self.nodes_evaluated = 0
            move, score, all_scores = self._minimax(
                game, 0, ai_player, ai_player, float('-inf'), float('inf'), 
                return_all_scores=True
            )
            trace = ThinkingTrace(
                move=move,
                score=score,
                nodes_evaluated=self.nodes_evaluated,
                branches_pruned=self.branches_pruned,
                max_depth_reached=self.max_depth_reached,
                evaluation_time_ms=(time.time() - start_time) * 1000,
                all_scores=all_scores
            )
        
        else:  # UNBEATABLE with Alpha-Beta
            self.nodes_evaluated = 0
            self.branches_pruned = 0
            move, score, all_scores = self._minimax_alpha_beta(
                game, 0, ai_player, ai_player, float('-inf'), float('inf'),
                return_all_scores=True
            )
            trace = ThinkingTrace(
                move=move,
                score=score,
                nodes_evaluated=self.nodes_evaluated,
                branches_pruned=self.branches_pruned,
                max_depth_reached=self.max_depth_reached,
                evaluation_time_ms=(time.time() - start_time) * 1000,
                all_scores=all_scores
            )
        
        self.last_trace = trace
        return move, trace
    
    def _one_ply_lookahead(self, game: TicTacToeGame, ai_player: Player) -> Tuple[int, int, List[MoveScore]]:
        """Evaluate only immediate next moves"""
        best_score = float('-inf')
        best_move = None
        all_scores = []
        
        for move in game.get_empty_cells():
            # Try move
            game_copy = copy.deepcopy(game)
            game_copy.make_move(move, ai_player)
            
            # Evaluate if AI wins immediately
            if game_copy.current_winner == ai_player:
                score = 10
            else:
                # Check if human can win next
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
        Pure Minimax algorithm (no pruning)
        Returns: (best_move, score, all_scores)
        """
        self.nodes_evaluated += 1
        self.max_depth_reached = max(self.max_depth_reached, depth)
        
        # Base cases
        if game.current_winner == ai_player:
            # AI wins: +10 - depth (prefers faster wins)
            return None, 10 - depth, None
        elif game.current_winner == ai_player.opposite():
            # Human wins: depth - 10 (prefers slower losses)
            return None, depth - 10, None
        elif game.is_full():
            return None, 0, None
        
        # Recursive case
        if current_player == ai_player:
            # Maximizing (AI wants high score)
            best_score = float('-inf')
            best_move = None
            all_scores = [] if return_all_scores else None
            
            for move in game.get_empty_cells():
                game_copy = copy.deepcopy(game)
                game_copy.make_move(move, current_player)
                
                _, score, _ = self._minimax(
                    game_copy, depth + 1, current_player.opposite(), 
                    ai_player, alpha, beta, False
                )
                
                if return_all_scores:
                    all_scores.append(MoveScore(position=move, score=score, depth=depth))
                
                if score > best_score:
                    best_score = score
                    best_move = move
                    
            return best_move, best_score, all_scores
        
        else:
            # Minimizing (human wants low score)
            best_score = float('inf')
            best_move = None
            all_scores = [] if return_all_scores else None
            
            for move in game.get_empty_cells():
                game_copy = copy.deepcopy(game)
                game_copy.make_move(move, current_player)
                
                _, score, _ = self._minimax(
                    game_copy, depth + 1, current_player.opposite(),
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
        Minimax with Alpha-Beta pruning
        Returns: (best_move, score, all_scores)
        """
        self.nodes_evaluated += 1
        self.max_depth_reached = max(self.max_depth_reached, depth)
        
        # Base cases
        if game.current_winner == ai_player:
            return None, 10 - depth, None
        elif game.current_winner == ai_player.opposite():
            return None, depth - 10, None
        elif game.is_full():
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
                    game_copy, depth + 1, current_player.opposite(),
                    ai_player, alpha, beta, False
                )
                
                if return_all_scores:
                    all_scores.append(MoveScore(position=move, score=score, depth=depth))
                
                if score > best_score:
                    best_score = score
                    best_move = move
                
                # Alpha-Beta pruning
                alpha = max(alpha, score)
                if beta <= alpha:
                    self.branches_pruned += 1
                    break
                    
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
                    game_copy, depth + 1, current_player.opposite(),
                    ai_player, alpha, beta, False
                )
                
                if return_all_scores:
                    all_scores.append(MoveScore(position=move, score=score, depth=depth))
                
                if score < best_score:
                    best_score = score
                    best_move = move
                
                # Alpha-Beta pruning
                beta = min(beta, score)
                if beta <= alpha:
                    self.branches_pruned += 1
                    break
                    
            return best_move, best_score, all_scores
    
    def get_move_scores_for_display(self, game: TicTacToeGame, ai_player: Player) -> List[MoveScore]:
        """Get scores for all empty cells (for heatmap display)"""
        if self.difficulty == Difficulty.EASY:
            return [MoveScore(pos, 0, 0) for pos in game.get_empty_cells()]
        
        elif self.difficulty == Difficulty.MEDIUM:
            _, _, scores = self._one_ply_lookahead(game, ai_player)
            return scores
        
        elif self.difficulty == Difficulty.HARD:
            # Reset counters
            old_nodes = self.nodes_evaluated
            old_pruned = self.branches_pruned
            self.nodes_evaluated = 0
            
            _, _, scores = self._minimax(
                game, 0, ai_player, ai_player, float('-inf'), float('inf'),
                return_all_scores=True
            )
            
            self.nodes_evaluated = old_nodes
            self.branches_pruned = old_pruned
            return scores if scores else []
        
        else:  # UNBEATABLE
            old_nodes = self.nodes_evaluated
            old_pruned = self.branches_pruned
            self.nodes_evaluated = 0
            
            _, _, scores = self._minimax_alpha_beta(
                game, 0, ai_player, ai_player, float('-inf'), float('inf'),
                return_all_scores=True
            )
            
            self.nodes_evaluated = old_nodes
            self.branches_pruned = old_pruned
            return scores if scores else []