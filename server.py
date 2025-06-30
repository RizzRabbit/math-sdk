from flask import Flask, request, jsonify
from flask_cors import CORS
import sys
import os

# Add the parent directory of games to the Python path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), 'games', 'the-rabbits-den')))
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), 'src')))

from game_config import GameConfig
from gamestate import GameState

app = Flask(__name__)
CORS(app)

# Initialize GameConfig and GameState once
config = GameConfig()
gamestate = GameState(config)

@app.route('/spin', methods=['POST'])
def spin_game():
    data = request.get_json()
    bet_amount = data.get('amount')
    mode = data.get('mode', 'BASE')

    # For now, we'll use a dummy sim object as run_spin expects it
    # In a real scenario, this might involve a seed or other simulation parameters
    class DummySim:
        def __init__(self):
            self.current_mode = mode
            self.current_bet = bet_amount
            self.current_seed = os.urandom(8).hex() # Generate a random seed
            self.sim = 0 # Add a sim attribute for GameState initialization

    sim = DummySim()

    try:
        # Execute a single spin
        gamestate.run_spin(sim)

        # Extract relevant data from gamestate after spin
        # This part needs to be adapted based on the actual structure of gamestate
        # after a spin in the math-sdk. I'm making assumptions here.
        initial_grid = gamestate.board.get_board()
        total_win_amount = gamestate.win_manager.total_win
        free_games_remaining = gamestate.fs
        

        # Simulate cascade results (math-sdk might provide this differently)
        cascade_results = []
        if gamestate.win_data and gamestate.win_data["wins"]:
            # This is a simplified representation. The math-sdk might have more detailed cascade info.
            cascade_results.append({
                "grid": gamestate.board.get_board(), # Grid after first win
                "winning_cells": [],
                "win_amount": gamestate.win_data["totalWin"], # Win from this cascade
                "message": "Win!"
            })
            for win in gamestate.win_data["wins"]:
                for pos in win["positions"]:
                    cascade_results[-1]["winning_cells"].append([pos["reel"], pos["row"]])


        response_data = {
            "initial_grid": initial_grid,
            "cascade_results": cascade_results,
            "total_win_amount": total_win_amount,
            "message": "Spin successful!",
            "free_games_remaining": free_games_remaining
        }
        return jsonify(response_data)

    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True, port=5001) # Run on a different port than the mock RGS server